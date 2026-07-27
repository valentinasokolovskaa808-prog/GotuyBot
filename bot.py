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

# --- ФЕЙКОВИЙ СЕРВЕР ДЛЯ БЕЗКОШТОВНОГО ТАРИФУ RENDER ---
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


# --- FSM (Стани) ---
class AddRecipeFSM(StatesGroup):
    title = State()
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

def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel")]
    ])


# --- ОБРОБНИКИ КОМАНД ---

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "Привіт! Вітаємо в «Готуй! Прості рецепти» 🍳\n\n"
        "Скористайтеся меню нижче або надішліть назву страви для пошуку:",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("admin"))
async def admin_handler(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Вітаю в панелі адміністратора! Оберіть дію:", reply_markup=get_admin_keyboard())
    else:
        await message.answer("У вас немає доступу до цієї команди.")


# --- СЦЕНАРІЙ ДОДАВАННЯ РЕЦЕПТУ ---

@dp.callback_query(F.data == "add_recipe")
async def start_add_recipe(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("Немає доступу.", show_alert=True)
    
    await state.set_state(AddRecipeFSM.title)
    await callback.message.answer("Крок 1/4: Введіть **назву рецепта**:", reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "stats")
async def stats_handler(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("Немає доступу.", show_alert=True)
    
    count = 0
    try:
        if hasattr(db, 'get_recipes_count'):
            count = db.get_recipes_count()
        elif hasattr(db, 'search_recipes'):
            all_res = db.search_recipes("")
            count = len(all_res) if all_res else 0
    except Exception as e:
        logger.error(f"Помилка статистики: {e}")

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
    await state.set_state(AddRecipeFSM.ingredients)
    await message.answer("Крок 2/4: Введіть **інгредієнти**:", reply_markup=get_cancel_keyboard(), parse_mode="Markdown")

@dp.message(AddRecipeFSM.ingredients)
async def process_ingredients(message: types.Message, state: FSMContext):
    await state.update_data(ingredients=message.text)
    await state.set_state(AddRecipeFSM.instructions)
    await message.answer("Крок 3/4: Введіть **інструкцію приготування**:", reply_markup=get_cancel_keyboard(), parse_mode="Markdown")

@dp.message(AddRecipeFSM.instructions)
async def process_instructions(message: types.Message, state: FSMContext):
    await state.update_data(instructions=message.text)
    await state.set_state(AddRecipeFSM.link)
    await message.answer("Крок 4/4: Введіть **посилання на відео** (або `-`):", reply_markup=get_cancel_keyboard(), parse_mode="Markdown")

@dp.message(AddRecipeFSM.link)
async def process_link(message: types.Message, state: FSMContext):
    link = message.text if message.text != "-" else ""
    user_data = await state.get_data()
    
    try:
        if hasattr(db, 'add_recipe'):
            db.add_recipe(
                title=user_data['title'],
                ingredients=user_data['ingredients'],
                instructions=user_data['instructions'],
                video_url=link,
                is_breakfast=1, # Робимо доступним за замовчуванням
                is_lunch=1,
                is_dinner=1,
                is_baking=1,
                is_desserts=1
            )

        await message.answer(f"✅ **Рецепт успішно додано!**\n📌 **Назва:** {user_data['title']}", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Помилка при додаванні: {e}")
        await message.answer(f"❌ Помилка: {e}")

    await state.clear()


# --- ДОПОМІЖНА ФУНКЦІЯ ВІДОБРАЖЕННЯ РЕЦЕПТІВ ---

async def fetch_and_send_recipes(message: types.Message, query: str):
    if hasattr(db, 'search_recipes'):
        try:
            results = db.search_recipes(query)
            if results:
                for recipe in results[:5]:
                    title = "Рецепт"
                    ingr = ""
                    instr = ""
                    url = ""

                    if isinstance(recipe, dict):
                        title = recipe.get('title') or recipe.get('name') or "Рецепт"
                        ingr = recipe.get('ingredients', '')
                        instr = recipe.get('instructions', '')
                        url = recipe.get('video_url') or recipe.get('link', '')
                    elif isinstance(recipe, (list, tuple)):
                        if len(recipe) > 1 and recipe[1]:
                            title = str(recipe[1])
                        if len(recipe) > 2 and recipe[2]:
                            ingr = str(recipe[2])
                        if len(recipe) > 3 and recipe[3]:
                            instr = str(recipe[3])
                        if len(recipe) > 4 and recipe[4]:
                            url = str(recipe[4])

                    if title == "Рецепт та деталі у відео" or title == "Рецепт":
                        if isinstance(recipe, (list, tuple)):
                            for item in recipe:
                                if isinstance(item, str) and item and not item.startswith("http") and item != "Дивіться відеорецепт у каналі":
                                    title = item
                                    break

                    text = f"🍳 **{title}**\n\n"
                    if ingr:
                        text += f"🛒 **Інгредієнти:**\n{ingr}\n\n"
                    if instr and not instr.startswith("http"):
                        text += f"👩‍🍳 **Приготування:**\n{instr}\n"
                    elif instr.startswith("http") and not url:
                        url = instr

                    if url and url != "-":
                        text += f"\n🔗 [Дивитися відео]({url})"

                    await message.answer(text, parse_mode="Markdown")
            else:
                await message.answer(f"Нічого не знайдено 😔 Спробуйте ввести назву конкретної страви або інгредієнт.")
        except Exception as e:
            logger.error(f"Помилка пошуку: {e}")
            await message.answer(f"❌ Помилка при пошуку: {e}")


# --- ОБРОБКА ВСІХ КНОПЕК МЕНЮ ---

@dp.message()
async def main_messages_handler(message: types.Message):
    text = message.text.strip()
    if not text or text.startswith("/"):
        return

    # 1. Спеціальна кнопка "Наші соцмережі"
    if "соцмережі" in text.lower() or "наші соцмережі" in text.lower():
        await message.answer(
            "📲 **Наші офіційні сторінки та канали:**\n\n"
            "🔹 **Telegram:** https://t.me/gotuyprostirecepty\n"
            "🔹 **TikTok:** шукайте нас під брендом «Готуй! Прості рецепти»\n\n"
            "Приєднуйтесь та готуйте разом з нами! 🍳",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return

    # 2. Кнопка "Пошук рецепту"
    if "пошук рецепту" in text.lower() or "пошук" in text.lower():
        await message.answer("🔍 Введіть назву страви або інгредієнт (наприклад: *лаваш*, *сир*, *курка*):", parse_mode="Markdown")
        return

    # 3. Кнопка "Відеорецепти"
    if "відеорецепти" in text.lower():
        await fetch_and_send_recipes(message, "http")
        return

    # 4. Категорії (очищаємо від будь-яких емодзі)
    clean_query = text
    for emoji in ["🍳", "🥗", "🥦", "🥐", "🍰", "🎬", "🔎", "📲", "👉", "✨", "☀️", "🌙", "🌅"]:
        clean_query = clean_query.replace(emoji, "")
    clean_query = clean_query.strip()

    # Шукаємо за очищеним словом (наприклад "Сніданок", "Випічка" або за тим словом, яке ввів користувач)
    await fetch_and_send_recipes(message, clean_query)


# --- ГОЛОВНА ФУНКЦІЯ ---

async def main():
    if hasattr(db, 'init_db'):
        db.init_db()

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("БОТ УСПІШНО ЗАПУЩЕНИЙ")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот зупинений.")
