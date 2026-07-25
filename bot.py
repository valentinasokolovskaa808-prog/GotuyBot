import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN
from keyboards.main_menu import main_menu, social_links_menu

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# --- Клас станів для пошуку ---
class SearchRecipe(StatesGroup):
    waiting_for_query = State()


# --- 1. Стандартна команда /start ---
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Ласкаво просимо до кулінарного бота «Готуй! Прості рецепти».\nОберіть потрібний розділ нижче:",
        reply_markup=main_menu
    )


# --- 2. Обробник кнопки "Наші соцмережі" ---
@dp.message(F.text.contains("соцмер"))
async def show_social_links(message: types.Message):
    await message.answer(
        "<b>Готуй! Прості рецепти</b> у соцмережах! 🍳\n\n"
        "Підписуйтесь, щоб дивитися нові відеорецепти:",
        reply_markup=social_links_menu,
        parse_mode="HTML"
    )


# --- 3. ОБРОБНИКИ ПОШУКУ (обов'язково ВИЩЕ за загальний обробник) ---
@dp.message(F.text.contains("Пошук рецепту"))
async def start_search(message: types.Message, state: FSMContext):
    await state.set_state(SearchRecipe.waiting_for_query)
    await message.answer(
        "🔍 <b>Введіть назву страви для пошуку:</b>\n<i>(наприклад: сирники, борщ, курка)</i>", 
        parse_mode="HTML"
    )


@dp.message(SearchRecipe.waiting_for_query)
async def process_search(message: types.Message, state: FSMContext):
    query = message.text.strip().lower()
    await state.clear()
    
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, description, url FROM recipes WHERE LOWER(name) LIKE ?", (f"%{query}%",))
        results = cursor.fetchall()
        conn.close()

        if not results:
            await message.answer(f"😔 На жаль, за запитом <b>«{query}»</b> нічого не знайдено.", parse_mode="HTML")
            return

        text = f"🔎 <b>Результати пошуку за запитом «{query}»:</b>\n\n"
        for name, desc, url in results:
            text += f"🔹 <b>{name}</b>\n{desc}\n🔗 {url}\n\n"

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"⚠️ Помилка бази даних:\n<code>{e}</code>", parse_mode="HTML")


# --- 4. Загальний обробник решти повідомлень ---
@dp.message()
async def echo_all(message: types.Message):
    await message.answer(f"Ви обрали: {message.text}")


# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())