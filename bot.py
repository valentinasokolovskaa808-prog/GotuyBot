import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import re

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN
from main_menu import main_menu, social_links_menu
from database import init_db, search_recipes, get_breakfast_recipes

# --- Заглушка сервера для Render ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- Ініціалізація бази даних ---
init_db()

# --- Налаштування бота ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class SearchRecipe(StatesGroup):
    waiting_for_query = State()

def clean_text(text: str) -> str:
    """Видаляє смайлики, хештеги та зайві пробіли для точного порівняння"""
    if not text:
        return ""
    # Видаляємо всі небуквені та нецифрові символи (включаючи emoji)
    cleaned = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
    return cleaned.strip().lower()

# --- 1. Команда /start ---
@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Ласкаво просимо до кулінарного бота «Готуй! Прості рецепти».\nОберіть потрібний розділ нижче:",
        reply_markup=main_menu
    )

# --- 2. Кнопка "Сніданок" та хештег #сніданок ---
@dp.message(F.text.func(lambda text: "сніданок" in clean_text(text)))
async def show_breakfast_recipes(message: types.Message, state: FSMContext):
    await state.clear()
    results = get_breakfast_recipes()
    
    await message.answer("🍳 <b>Чудові варіанти рецептів для сніданку:</b>", parse_mode="HTML")
    
    for title, ingredients, instructions, video_url in results:
        text = f"🍳 <b>{title}</b>\n\n"
        text += f"🛒 <b>Інгредієнти:</b>\n{ingredients}\n\n"
        text += f"👨‍🍳 <b>Приготування:</b>\n{instructions}"
        
        if video_url:
            text += f"\n\n▶️ <a href='{video_url}'>Дивитися відеорецепт</a>"
            
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

# --- 3. Кнопка "Наші соцмережі" ---
@dp.message(F.text.func(lambda text: "соцмереж" in clean_text(text)))
async def show_social_links(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>Готуй! Прості рецепти</b> у соцмережах! 🔍\n\n"
        "Підписуйтесь, щоб дивитися нові відеорецепти:",
        reply_markup=social_links_menu,
        parse_mode="HTML"
    )

# --- 4. Старт пошуку за кнопкою "Пошук рецепту" ---
@dp.message(F.text.func(lambda text: "пошук" in clean_text(text)))
async def start_search(message: types.Message, state: FSMContext):
    await state.set_state(SearchRecipe.waiting_for_query)
    await message.answer(
        "🔎 <b>Введіть назву страви або інгредієнт</b> (наприклад: <i>чебуреки</i>, <i>салат</i> або <i>курка</i>):",
        parse_mode="HTML"
    )

# --- 5. Обробка пошукового запиту у стані очікування ---
@dp.message(SearchRecipe.waiting_for_query)
async def process_search(message: types.Message, state: FSMContext):
    raw_query = message.text.strip()
    cleaned_q = clean_text(raw_query)
    
    # Якщо шукають сніданок
    if "сніданок" in cleaned_q:
        await show_breakfast_recipes(message, state)
        return
        
    results = search_recipes(raw_query)
    
    if not results:
        await message.answer(
            f"❌ На жаль, за запитом <b>«{raw_query}»</b> нічого не знайдено.\nСпробуйте ввести іншу назву або інгредієнт:",
            parse_mode="HTML"
        )
        return
    
    for title, ingredients, instructions, video_url in results:
        text = f"🍳 <b>{title}</b>\n\n"
        text += f"🛒 <b>Інгредієнти:</b>\n{ingredients}\n\n"
        text += f"👨‍🍳 <b>Приготування:</b>\n{instructions}"
        
        if video_url:
            text += f"\n\n▶️ <a href='{video_url}'>Дивитися відеорецепт</a>"
            
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
    
    await state.clear()

# --- 6. Пошук за звичайним текстом (без стану) ---
@dp.message(F.text)
async def default_text_search(message: types.Message, state: FSMContext):
    raw_query = message.text.strip()
    cleaned_q = clean_text(raw_query)
    
    # Якщо написано сніданок / #сніданок / 🍳 Сніданок
    if "сніданок" in cleaned_q:
        await show_breakfast_recipes(message, state)
        return

    results = search_recipes(raw_query)
    
    if results:
        for title, ingredients, instructions, video_url in results:
            text = f"🍳 <b>{title}</b>\n\n"
            text += f"🛒 <b>Інгредієнти:</b>\n{ingredients}\n\n"
            text += f"👨‍🍳 <b>Приготування:</b>\n{instructions}"
            
            if video_url:
                text += f"\n\n▶️ <a href='{video_url}'>Дивитися відеорецепт</a>"
                
            await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
    else:
        await message.answer(
            "Скористайтеся кнопками меню нижче або введіть назву страви для пошуку (наприклад: <i>чебуреки</i>, <i>салат</i>, <i>деруни</i>):",
            reply_markup=main_menu,
            parse_mode="HTML"
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
