import os
import re
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
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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

# Запускаємо фейковий сервер в окремому потоці
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
        "Привіт! Я ваш кулінарний бот 🍳\n\n"
        "Введіть назву страви або інгредієнти, щоб знайти рецепт."
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

@dp.callback_query(F.data == "cancel")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Додавання рецепта скасовано.", reply_markup=get_admin_keyboard())
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
                link=link
            )

        await message.answer(
            f"✅ **Рецепт успішно додано!**\n\n"
            f"📌 **Назва:** {user_data['title']}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Помилка: {e}")
        await message.answer(f"❌ Помилка: {e}")

    await state.clear()


# --- ПОШУК РЕЦЕПТІВ ---

@dp.message()
async def search_handler(message: types.Message):
    query = message.text.strip()
    if not query:
        return

    if hasattr(db, 'search_recipes'):
        results = db.search_recipes(query)
        if results:
            for recipe in results[:3]:
                text = f"🍳 **{recipe.get('title', 'Рецепт')}**\n\n"
                if 'ingredients' in recipe:
                    text += f"🛒 **Інгредієнти:**\n{recipe['ingredients']}\n\n"
                if 'instructions' in recipe:
                    text += f"👩‍🍳 **Приготування:**\n{recipe['instructions']}\n"
                if recipe.get('link'):
                    text += f"\n🔗 [Дивитися відео]({recipe['link']})"

                await message.answer(text, parse_mode="Markdown")
        else:
            await message.answer("Нічого не знайдено 😔")


# --- ГОЛОВНА ФУНКЦІЯ ---

async def main():
    if hasattr(db, 'init_db'):
        db.init_db()

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("БОТ З АДМІН-ПАНЕЛЛЮ УСПІШНО ЗАПУЩЕНИЙ")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот зупинений.")
