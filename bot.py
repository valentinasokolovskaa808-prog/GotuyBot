import os
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Dummy HTTP Server для Web Service на Render ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
        
    def log_message(self, format, *args):
        return

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Starting dummy HTTP server on port {port}")
    server.serve_forever()

server_thread = threading.Thread(target=run_dummy_server, daemon=True)
server_thread.start()

# --- Імпорти Aiogram та модулів ---
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN
from main_menu import main_menu, social_links_menu
import database

# Ініціалізація БД
try:
    database.init_db()
    logger.info("Database initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class SearchRecipe(StatesGroup):
    waiting_for_query = State()

def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
    return cleaned.strip().lower()

async def send_recipe_list(message: types.Message, title_header: str, recipes: list):
    await message.answer(title_header, parse_mode="HTML")
    for title, ingredients, instructions, video_url in recipes:
        text = f"🍳 <b>{title}</b>\n\n"
        text += f"🛒 <b>Інгредієнти:</b>\n{ingredients}\n\n"
        text += f"👨‍🍳 <b>Приготування:</b>\n{instructions}"
        
        if video_url:
            text += f"\n\n▶️ <a href='{video_url}'>Дивитися відеорецепт</a>"
            
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Ласкаво просимо до кулінарного бота «Готуй! Прості рецепти».\nОберіть потрібний розділ нижче:",
        reply_markup=main_menu
    )

# --- Категорії ---
@dp.message(F.text.func(lambda text: "сніданок" in clean_text(text)))
async def show_breakfast_recipes(message: types.Message, state: FSMContext):
    await state.clear()
    results = database.get_breakfast_recipes()
    await send_recipe_list(message, "🍳 <b>Чудові варіанти рецептів для сніданку:</b>", results)

@dp.message(F.text.func(lambda text: "обід" in clean_text(text)))
async def show_lunch_recipes(message: types.Message, state: FSMContext):
    await state.clear()
    results = database.get_lunch_recipes()
    await send_recipe_list(message, "🍲 <b>Смачні варіанти рецептів для обіду:</b>", results)

@dp.message(F.text.func(lambda text: "вечеря" in clean_text(text)))
async def show_dinner_recipes(message: types.Message, state: FSMContext):
    await state.clear()
    results = database.get_dinner_recipes()
    await send_recipe_list(message, "🥗 <b>Легкі та смачні варіанти рецептів для вечері:</b>", results)

@dp.message(F.text.func(lambda text: "випічка" in clean_text(text)))
async def show_baking_recipes(message: types.Message, state: FSMContext):
    await state.clear()
    results = database.get_baking_recipes()
    await send_recipe_list(message, "🥐 <b>Смачна та ароматна випічка:</b>", results)

@dp.message(F.text.func(lambda text: "десерт" in clean_text(text)))
async def show_dessert_recipes(message: types.Message, state: FSMContext):
    await state.clear()
    results = database.get_dessert_recipes()
    await send_recipe_list(message, "🍰 <b>Найкращі солодкі десерти:</b>", results)

@dp.message(F.text.func(lambda text: "відео" in clean_text(text)))
async def show_video_recipes(message: types.Message, state: FSMContext):
    await state.clear()
    results = database.get_video_recipes()
    await send_recipe_list(message, "🎬 <b>Рецепти з короткими відеоуроками:</b>", results)

@dp.message(F.text.func(lambda text: "соцмереж" in clean_text(text)))
async def show_social_links(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>Готуй! Прості рецепти</b> у соцмережах! 🔍\n\n"
        "Підписуйтесь, щоб дивитися нові відеорецепти:",
        reply_markup=social_links_menu,
        parse_mode="HTML"
    )

@dp.message(F.text.func(lambda text: "пошук" in clean_text(text)))
async def start_search(message: types.Message, state: FSMContext):
    await state.set_state(SearchRecipe.waiting_for_query)
    await message.answer(
        "🔎 <b>Введіть назву страви або інгредієнт</b> (наприклад: <i>чебуреки</i>, <i>салат</i> або <i>курка</i>):",
        parse_mode="HTML"
    )

@dp.message(SearchRecipe.waiting_for_query)
async def process_search(message: types.Message, state: FSMContext):
    raw_query = message.text.strip()
    cleaned_q = clean_text(raw_query)
    
    if "сніданок" in cleaned_q:
        await show_breakfast_recipes(message, state)
        return
    elif "обід" in cleaned_q:
        await show_lunch_recipes(message, state)
        return
    elif "вечеря" in cleaned_q:
        await show_dinner_recipes(message, state)
        return
    elif "випічка" in cleaned_q:
        await show_baking_recipes(message, state)
        return
    elif "десерт" in cleaned_q:
        await show_dessert_recipes(message, state)
        return
    elif "відео" in cleaned_q:
        await show_video_recipes(message, state)
        return
        
    results = database.search_recipes(raw_query)
    
    if not results:
        await message.answer(
            f"❌ На жаль, за запитом <b>«{raw_query}»</b> нічого не знайдено.\nСпробуйте ввести іншу назву або інгредієнт:",
            parse_mode="HTML"
        )
        return
    
    await send_recipe_list(message, f"🔎 <b>Результати пошуку за запитом «{raw_query}»:</b>", results)
    await state.clear()

@dp.message(F.text)
async def default_text_search(message: types.Message, state: FSMContext):
    raw_query = message.text.strip()
    cleaned_q = clean_text(raw_query)
    
    if "сніданок" in cleaned_q:
        await show_breakfast_recipes(message, state)
        return
    elif "обід" in cleaned_q:
        await show_lunch_recipes(message, state)
        return
    elif "вечеря" in cleaned_q:
        await show_dinner_recipes(message, state)
        return
    elif "випічка" in cleaned_q:
        await show_baking_recipes(message, state)
        return
    elif "десерт" in cleaned_q:
        await show_dessert_recipes(message, state)
        return
    elif "відео" in cleaned_q:
        await show_video_recipes(message, state)
        return

    results = database.search_recipes(raw_query)
    
    if results:
        await send_recipe_list(message, f"🔎 <b>Результати пошуку за запитом «{raw_query}»:</b>", results)
    else:
        await message.answer(
            "Скористайтеся кнопками меню нижче або введіть назву страви для пошуку (наприклад: <i>чебуреки</i>, <i>салат</i>, <i>деруни</i>):",
            reply_markup=main_menu,
            parse_mode="HTML"
        )

async def main():
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
