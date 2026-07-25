import asyncio
import logging
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN
from main_menu import main_menu, social_links_menu

# --- Заглушка сервера для Render (щоб пройти перевірку порту) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

# Запускаємо сервер у фоновому потоці
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- Основний код бота ---
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
@dp.message(F.text.contains("соцмереж"))
async def show_social_links(message: types.Message):
    await message.answer(
        "<b>Готуй! Прості рецепти</b> у соцмережах! 🔍\n\n"
        "Підписуйтесь, щоб дивитися нові відеорецепти:",
        reply_markup=social_links_menu,
        parse_mode="HTML"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
