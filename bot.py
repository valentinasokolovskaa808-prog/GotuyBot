import os
import asyncio
import logging
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

import database
from database import init_db, search_recipes, get_connection
from main_menu import main_menu, social_links_menu

# --- Налаштування логування ---
logging.basicConfig(level=logging.INFO)

# --- Токен та ID Адміністратора ---
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено в змінних оточення")

ADMIN_ID = 5270272994  # Ваш особистий Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# --- Заглушка веб-сервера для Render ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()


# --- Функції для бази даних користувачів ---
def init_users_table():
    """Створює таблицю users, якщо її ще немає."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id: int, username: str, first_name: str):
    """Зберігає користувача в базі."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
    ''', (user_id, username, first_name))
    conn.commit()
    conn.close()

def get_all_users():
    """Отримує всіх користувачів для розсилки."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users]

def get_users_count():
    """Отримує кількість підписників."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# --- Ініціалізація баз даних ---
init_db()
init_users_table()


# --- Стани FSM ---
class SearchRecipe(StatesGroup):
    waiting_for_query = State()


# --- 1. Команда /start ---
@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Записуємо користувача в БД
    add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    await message.answer(
        "Ласкаво просимо до кулінарного бота «Готуй! Прості рецепти».\nОберіть потрібний розділ нижче:",
        reply_markup=main_menu
    )


# --- 2. Статистика (команда /stats або кнопка "Статистика") ---
@dp.message(F.text.contains("Статистика") | Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    total_users = get_users_count()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM recipes")
    total_recipes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_breakfast = 1")
    breakfasts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_lunch = 1")
    lunches = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_dinner = 1")
    dinners = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_baking = 1")
    baking = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_desserts = 1")
    desserts = cursor.fetchone()[0]
    
    conn.close()

    text = (
        f"📊 <b>Загальна статистика бота:</b>\n\n"
        f"👥 <b>Користувачів у базі:</b> {total_users}\n\n"
        f"📖 <b>Всього рецептів:</b> {total_recipes}\n"
        f"• Сніданки: {breakfasts}\n"
        f"• Обіди: {lunches}\n"
        f"• Вечері: {dinners}\n"
        f"• Випічка: {baking}\n"
        f"• Десерти: {desserts}"
    )
    
    await message.answer(text, parse_mode="HTML")


# --- 3. Розсилка /broadcast ---
@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    text_to_send = message.text.replace("/broadcast", "").strip()
    
    if not text_to_send:
        await message.answer("⚠️ Введіть текст після команди.\n\nПриклад:\n<code>/broadcast Привіт усім! Новий рецепт уже на каналі!</code>", parse_mode="HTML")
        return

    users = get_all_users()
    await message.answer(f"🚀 Розпочато розсилку для {len(users)} користувачів...")
    
    success = 0
    blocked = 0

    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=text_to_send, parse_mode="HTML")
            success += 1
            await asyncio.sleep(0.04)
        except Exception:
            blocked += 1

    await message.answer(
        f"✅ <b>Розсилку завершено!</b>\n\n"
        f"✉️ Доставлено: <b>{success}</b>\n"
        f"🚫 Заблокували бота: <b>{blocked}</b>",
        parse_mode="HTML"
    )


# --- 4. Кнопка "Наші соцмережі" ---
@dp.message(F.text.contains("соцмереж"))
async def show_social_links(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>Готуй! Прості рецепти</b> у соцмережах! 🔍\n\n"
        "Підписуйтесь, щоб дивитися нові відеорецепти:",
        reply_markup=social_links_menu,
        parse_mode="HTML"
    )


# --- 5. Пошук рецепту ---
@dp.message(F.text.contains("Пошук") | F.text.contains("пошук"))
async def start_search(message: types.Message, state: FSMContext):
    await state.set_state(SearchRecipe.waiting_for_query)
    await message.answer(
        "🔎 <b>Введіть назву страви або інгредієнт</b> (наприклад: <i>чебуреки</i>, <i>салат</i> або <i>курка</i>):",
        parse_mode="HTML"
    )


# --- 6. Обробка тексту пошуку у стані SearchRecipe ---
@dp.message(SearchRecipe.waiting_for_query)
async def process_search(message: types.Message, state: FSMContext):
    query = message.text.strip()
    results = search_recipes(query)
    
    if not results:
        await message.answer(
            f"❌ На жаль, за запитом <b>«{query}»</b> нічого не знайдено.\nСпробуйте ввести іншу назву або інгредієнт:",
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


# --- 7. Загальний пошук за звичайним текстом ---
@dp.message(F.text)
async def default_text_search(message: types.Message, state: FSMContext):
    query = message.text.strip()
    results = search_recipes(query)
    
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
    # Видаляємо вебхуки та скидаємо чергу, щоб уникнути TelegramConflictError
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
