import os
import asyncio
import logging
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, ADMIN_IDS
import database as db

# --- ФЕЙКОВИЙ СЕРВЕР ДЛЯ BIND PORT НА RENDER ---
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()


# --- НАЛАШТУВАННЯ ЛОГІВ ТА БОТА ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# --- FSM (Стани додавання рецепту) ---
class AddRecipeFSM(StatesGroup):
    title = State()
    category = State()
    ingredients = State()
    instructions = State()
    link = State()


# --- КЛАВІАТУРИ ---

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍳 Сніданок"), KeyboardButton(text="🥗 Обід"), KeyboardButton(text="🥦 Вечеря")],
            [KeyboardButton(text="🥐 Випічка"), KeyboardButton(text="🍰 Десерти")],
            [KeyboardButton(text="🎬 Відеорецепти"), KeyboardButton(text="🔎 Пошук рецепту")],
            [KeyboardButton(text="📲 Наші соцмережі")]
        ],
        resize_keyboard=True
    )

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати рецепт", callback_data="add_recipe")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")]
    ])

def get_category_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍳 Сніданок", callback_data="cat_breakfast"), InlineKeyboardButton(text="🥗 Обід", callback_data="cat_lunch")],
        [InlineKeyboardButton(text="🥦 Вечеря", callback_data="cat_dinner"), InlineKeyboardButton(text="🥐 Випічка", callback_data="cat_baking")],
        [InlineKeyboardButton(text="🍰 Десерти", callback_data="cat_desserts")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel")]
    ])

def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel")]
    ])

def get_social_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 Telegram канал", url="https://t.me/gotuy_prosti_recepty")],
        [InlineKeyboardButton(text="🔹 TikTok", url="https://www.tiktok.com/@vitaly_is_cooking")],
        [InlineKeyboardButton(text="🔹 Instagram", url="https://www.instagram.com/vitaly_is_cooking/")],
        [InlineKeyboardButton(text="🔹 Facebook", url="https://www.facebook.com/GotuyProstiRecepty")]
    ])


# --- ОБРОБНИКИ КОМАНД ---

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "Привіт! Вітаємо в «Готуй! Прості рецепти» 🍳\n\n"
        "Оберіть категорію в меню нижче або напишіть назву страви для пошуку:",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("admin"))
async def admin_handler(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Вітаю в панелі адміністратора! Оберіть дію:", reply_markup=get_admin_keyboard())
    else:
        await message.answer("У вас немає доступу до цієї команди.")


# --- СЦЕНАРІЙ АДМІНІСТРАТОРА (ДОДАВАННЯ РЕЦЕПТУ) ---

@dp.callback_query(F.data == "add_recipe")
async def start_add_recipe(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("Немає доступу.", show_alert=True)
    
    await state.set_state(AddRecipeFSM.title)
    await callback.message.answer("Крок 1/5: Введіть **назву рецепта**:", reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "stats")
async def stats_handler(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("Немає доступу.", show_alert=True)
    
    count = len(db.get_video_recipes()) if hasattr(db, 'get_video_recipes') else 0
    await callback.message.answer(f"📊 **Статистика бази даних:**\n\nВсього рецептів у базі: **{count}**", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "cancel")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Скасовано.", reply_markup=get_admin_keyboard())
    await callback.answer()

@dp.message(AddRecipeFSM.title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddRecipeFSM.category)
    await message.answer("Крок 2/5: Оберіть **категорію** рецепта:", reply_markup=get_category_keyboard())

@dp.callback_query(AddRecipeFSM.category, F.data.startswith("cat_"))
async def process_category(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.replace("cat_", "")
    await state.update_data(category=category)
    await state.set_state(AddRecipeFSM.ingredients)
    await callback.message.answer("Крок 3/5: Введіть **інгредієнти** (або напишіть *Рецепт та деталі у відео*):", reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.message(AddRecipeFSM.ingredients)
async def process_ingredients(message: types.Message, state: FSMContext):
    await state.update_data(ingredients=message.text)
    await state.set_state(AddRecipeFSM.instructions)
    await message.answer("Крок 4/5: Введіть **інструкцію приготування** (або *Дивіться відеорецепт у каналі*):", reply_markup=get_cancel_keyboard(), parse_mode="Markdown")

@dp.message(AddRecipeFSM.instructions)
async def process_instructions(message: types.Message, state: FSMContext):
    await state.update_data(instructions=message.text)
    await state.set_state(AddRecipeFSM.link)
    await message.answer("Крок 5/5: Введіть **посилання на відео в Telegram**:", reply_markup=get_cancel_keyboard(), parse_mode="Markdown")

@dp.message(AddRecipeFSM.link)
async def process_link(message: types.Message, state: FSMContext):
    link = message.text.strip()
    user_data = await state.get_data()
    
    try:
        db.add_recipe(
            title=user_data['title'],
            ingredients=user_data['ingredients'],
            instructions=user_data['instructions'],
            video_url=link,
            category=user_data.get('category', 'baking')
        )
        await message.answer(f"✅ **Рецепт успішно додано!**\n📌 **Назва:** {user_data['title']}", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Помилка при додаванні: {e}")
        await message.answer(f"❌ Помилка: {e}")

    await state.clear()


# --- ДОПОМІЖНА ФУНКЦІЯ ДЛЯ ВІДОБРАЖЕННЯ КАРТОК РЕЦЕПТІВ ---

async def send_recipe_list(message: types.Message, recipes_list: list):
    if not recipes_list:
        await message.answer("У цій категорії поки немає доданих рецептів 😔")
        return

    for recipe in recipes_list[:5]:
        title = recipe[0]
        ingredients = recipe[1]
        instructions = recipe[2]
        video_url = recipe[3]

        text = f"🍳 **{title}**\n\n"
        
        if ingredients and ingredients != "Рецепт та деталі у відео":
            text += f"🛒 **Інгредієнти:**\n{ingredients}\n\n"
            
        if instructions and instructions != "Дивіться відеорецепт у каналі":
            text += f"👩‍🍳 **Приготування:**\n{instructions}\n\n"
            
        if video_url:
            text += f"🔗 [Переглянути відеорецепт]({video_url})"

        await message.answer(text, parse_mode="Markdown", disable_web_page_preview=False)


# --- ОСНОВНИЙ ОБРОБНИК КНОПЕК ТА ПОВІДОМЛЕНЬ ---

@dp.message()
async def main_handler(message: types.Message):
    text = message.text.strip() if message.text else ""
    if not text or text.startswith("/"):
        return

    text_lower = text.lower()

    # 1. Сніданок
    if "сніданок" in text_lower:
        recipes = db.get_breakfast_recipes()
        await send_recipe_list(message, recipes)

    # 2. Обід
    elif "обід" in text_lower:
        recipes = db.get_lunch_recipes()
        await send_recipe_list(message, recipes)

    # 3. Вечеря
    elif "вечеря" in text_lower:
        recipes = db.get_dinner_recipes()
        await send_recipe_list(message, recipes)

    # 4. Випічка
    elif "випічка" in text_lower:
        recipes = db.get_baking_recipes()
        await send_recipe_list(message, recipes)

    # 5. Десерти
    elif "десерт" in text_lower:
        recipes = db.get_dessert_recipes()
        await send_recipe_list(message, recipes)

    # 6. Відеорецепти
    elif "відеорецепти" in text_lower:
        recipes = db.get_video_recipes()
        await send_recipe_list(message, recipes)

    # 7. Пошук рецепту
    elif "пошук рецепту" in text_lower or "пошук" in text_lower:
        await message.answer(
            "🔍 **Як шукати?**\n\n"
            "Просто напишіть у чат назву страви або інгредієнт.\n"
            "Наприклад: *курка*, *салат*, *кекс*, *картопля*",
            parse_mode="Markdown"
        )

    # 8. Наші соцмережі
    elif "соцмережі" in text_lower:
        await message.answer(
            "📲 **Наші офіційні сторінки та канали:**\n\n"
            "Натискайте на кнопки нижче, щоб швидко перейти до потрібної спільноти 👇",
            reply_markup=get_social_keyboard(),
            parse_mode="Markdown"
        )

    # 9. Текстовий пошук за назвою або інгредієнтом
    else:
        results = db.search_recipes(text)
        if results:
            await send_recipe_list(message, results)
        else:
            await message.answer(
                f"Нічого не знайдено за запитом **«{text}»** 😔\n\n"
                f"Спробуйте ввести інше слово (наприклад, *салат*, *сир*, *курка*).",
                parse_mode="Markdown"
            )


# --- ЗАПУСК БОТА ---

async def main():
    if hasattr(db, 'init_db'):
        db.init_db()

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("БОТ УСПІШНО ЗАПУЩЕНИЙ В РЕЖИМІ POLLING")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот зупинений.")
