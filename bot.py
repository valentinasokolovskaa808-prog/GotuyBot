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
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, ADMIN_IDS
from main_menu import main_menu, social_links_menu, cancel_menu, skip_video_menu
import database

# Ініціалізація БД
try:
    database.init_db()
    logger.info("Database initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Стейти для FSM
class SearchRecipe(StatesGroup):
    waiting_for_query = State()

class AddRecipe(StatesGroup):
    title = State()
    ingredients = State()
    instructions = State()
    video_url = State()
    categories = State()

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

# --- Скасування дії ---
@dp.message(F.text == "❌ Скасувати")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Дію скасовано.", reply_markup=main_menu)

# --- Команда /start ---
@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Ласкаво просимо до кулінарного бота «Готуй! Прості рецепти».\nОберіть потрібний розділ нижче:",
        reply_markup=main_menu
    )

# --- АДМІН-ПАНЕЛЬ ---
@dp.message(Command("admin"))
async def admin_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас немає прав доступу до панелі адміністратора.")
        return

    await state.set_state(AddRecipe.title)
    await message.answer(
        "👑 <b>Панель додавання нового рецепта</b>\n\nВведіть <b>назву</b> рецепта:",
        parse_mode="HTML",
        reply_markup=cancel_menu
    )

@dp.message(AddRecipe.title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddRecipe.ingredients)
    await message.answer("🛒 Введіть <b>інгредієнти</b> (або вкажіть 'Рецепт та деталі у відео'):", parse_mode="HTML")

@dp.message(AddRecipe.ingredients)
async def process_ingredients(message: types.Message, state: FSMContext):
    await state.update_data(ingredients=message.text.strip())
    await state.set_state(AddRecipe.instructions)
    await message.answer("👨‍🍳 Введіть <b>інструкцію з приготування</b> (або 'Дивіться відеорецепт у каналі'):", parse_mode="HTML")

@dp.message(AddRecipe.instructions)
async def process_instructions(message: types.Message, state: FSMContext):
    await state.update_data(instructions=message.text.strip())
    await state.set_state(AddRecipe.video_url)
    await message.answer(
        "▶️ Введіть <b>посилання на відеорецепт</b> (наприклад, https://t.me/gotuy_prosti_recepty/1999) або натисніть «Пропустити відео»:",
        parse_mode="HTML",
        reply_markup=skip_video_menu
    )

def get_category_keyboard(selected: dict):
    def check_mark(val):
        return "✅" if val else "❌"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{check_mark(selected['breakfast'])} Сніданок", callback_data="toggle_breakfast")],
        [InlineKeyboardButton(text=f"{check_mark(selected['lunch'])} Обід", callback_data="toggle_lunch")],
        [InlineKeyboardButton(text=f"{check_mark(selected['dinner'])} Вечеря", callback_data="toggle_dinner")],
        [InlineKeyboardButton(text=f"{check_mark(selected['baking'])} Випічка", callback_data="toggle_baking")],
        [InlineKeyboardButton(text=f"{check_mark(selected['desserts'])} Десерти", callback_data="toggle_desserts")],
        [InlineKeyboardButton(text="💾 Зберегти рецепт", callback_data="save_recipe")]
    ])
    return kb

@dp.message(AddRecipe.video_url)
async def process_video(message: types.Message, state: FSMContext):
    url = message.text.strip()
    if url == "Пропустити відео":
        url = ""
    
    await state.update_data(video_url=url)
    
    categories = {
        'breakfast': 0,
        'lunch': 0,
        'dinner': 0,
        'baking': 0,
        'desserts': 0
    }
    await state.update_data(categories=categories)
    await state.set_state(AddRecipe.categories)
    
    await message.answer(
        "📌 Оберіть <b>категорії</b> для цього рецепта (можна обрати декілька) та натисніть <b>Зберегти рецепт</b>:",
        reply_markup=get_category_keyboard(categories),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("toggle_"))
async def toggle_category(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    categories = data.get("categories", {})
    cat_key = callback.data.replace("toggle_", "")
    
    if cat_key in categories:
        categories[cat_key] = 1 if categories[cat_key] == 0 else 0
        await state.update_data(categories=categories)
        await callback.message.edit_reply_markup(reply_markup=get_category_keyboard(categories))
    await callback.answer()

@dp.callback_query(F.data == "save_recipe")
async def save_recipe_callback(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cats = data.get("categories", {})
    
    database.add_recipe(
        title=data.get("title"),
        ingredients=data.get("ingredients"),
        instructions=data.get("instructions"),
        video_url=data.get("video_url"),
        is_breakfast=cats.get("breakfast", 0),
        is_lunch=cats.get("lunch", 0),
        is_dinner=cats.get("dinner", 0),
        is_baking=cats.get("baking", 0),
        is_desserts=cats.get("desserts", 0)
    )
    
    await callback.message.edit_text(f"✅ Рецепт <b>«{data.get('title')}»</b> успішно збережено в базу!", parse_mode="HTML")
    await callback.message.answer("Головне меню:", reply_markup=main_menu)
    await state.clear()
    await callback.answer()

# --- Клієнтські категорії ---
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
