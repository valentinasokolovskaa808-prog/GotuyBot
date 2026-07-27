import os
import logging
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Отримання токена з змінних середовища Render
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено в змінних оточення!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Імпорт функцій бази даних
import database

# Ініціалізація бази даних при запуску
database.init_db()


# --- Веб-сервер для підтримання роботи на Render ---
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        # Приглушуємо стандартні логи HTTP-сервера, щоб не засмічувати консоль
        return


def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()


# --- Клавіатури ---
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🍳 Сніданки", callback_data="cat_breakfast"
                ),
                InlineKeyboardButton(text="🍲 Обіди", callback_data="cat_lunch"),
            ],
            [
                InlineKeyboardButton(
                    text="🥗 Вечері", callback_data="cat_dinner"
                ),
                InlineKeyboardButton(
                    text="🥐 Випічка", callback_data="cat_baking"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🍰 Десерти", callback_data="cat_desserts"
                ),
                InlineKeyboardButton(
                    text="🎥 Відео-рецепти", callback_data="cat_video"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Як шукати?", callback_data="how_to_search"
                )
            ],
        ]
    )
    return keyboard


# --- Обробники команд та повідомлень ---


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    welcome_text = (
        f"Привіт, {message.from_user.first_name}! 👋\n\n"
        f"Ласкаво просимо до бота каналу **«Готуй! Прості рецепти»**! 🍳\n\n"
        f"Тут ви можете знайти смачні рецепти за категоріями або скористатися пошуком.\n"
        f"Просто напишіть назву страви або інгредієнт (наприклад: *сир*, *котлети*, *салат*), і я знайду відповідні рецепти!"
    )
    await message.answer(
        welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard()
    )


@dp.callback_query(F.data == "how_to_search")
async def process_how_to_search(callback: types.CallbackQuery):
    await callback.answer()
    info_text = (
        "💡 **Як користуватися пошуком:**\n\n"
        "Надішліть у чат будь-яке слово або назву страви:\n"
        "• `пиріг` — знайде всі пироги\n"
        "• `куряче` — знайде страви з куркою\n"
        "• `салат` — знайде відповідні салати\n\n"
        "Або обирайте потрібну категорію з меню нижче!"
    )
    await callback.message.answer(
        info_text, parse_mode="Markdown", reply_markup=get_main_keyboard()
    )


def format_recipe_list(recipes, title):
    if not recipes:
        return f"У категорії **{title}** поки немає рецептів."

    text = f"📋 **Категорія: {title}**\n\n"
    for r in recipes:
        recipe_title, ingredients, instructions, video_url = r
        text += f"🔹 **{recipe_title}**\n"
        if video_url:
            text += f"🔗 [Дивитися відеорецепт]({video_url})\n"
        text += "───────────────\n"
    return text


@dp.callback_query(F.data.startswith("cat_"))
async def process_category(callback: types.CallbackQuery):
    await callback.answer()
    cat = callback.data.split("_")[1]

    if cat == "breakfast":
        recipes = database.get_breakfast_recipes()
        title = "Сніданки"
    elif cat == "lunch":
        recipes = database.get_lunch_recipes()
        title = "Обіди"
    elif cat == "dinner":
        recipes = database.get_dinner_recipes()
        title = "Вечері"
    elif cat == "baking":
        recipes = database.get_baking_recipes()
        title = "Випічка"
    elif cat == "desserts":
        recipes = database.get_dessert_recipes()
        title = "Десерти"
    elif cat == "video":
        recipes = database.get_video_recipes()
        title = "Відео-рецепти"
    else:
        recipes = []
        title = "Невідома категорія"

    text = format_recipe_list(recipes, title)

    # Якщо текст занадто довгий для одного повідомлення, розбиваємо його
    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            await callback.message.answer(
                text[i : i + 4000],
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
    else:
        await callback.message.answer(
            text, parse_mode="Markdown", disable_web_page_preview=True
        )


@dp.message()
async def search_handler(message: types.Message):
    query = message.text
    if not query:
        return

    results = database.search_recipes(query)

    if not results:
        await message.answer(
            f"🔍 За запитом *«{query}»* нічого не знайдено.\nСпробуйте ввести інше слово або скористайтеся категоріями нижче.",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(),
        )
        return

    text = f"🔎 **Результати пошуку за запитом «{query}» ({len(results)}):**\n\n"
    for r in results:
        recipe_title, ingredients, instructions, video_url = r
        text += f"🔹 **{recipe_title}**\n"
        if video_url:
            text += f"🔗 [Дивитися відеорецепт]({video_url})\n"
        text += "───────────────\n"

    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            await message.answer(
                text[i : i + 4000],
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
    else:
        await message.answer(
            text, parse_mode="Markdown", disable_web_page_preview=True
        )


# --- Запуск бота ---
async def main():
    # Запускаємо веб-сервер у фоновому потоці для Render
    server_thread = Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    logging.info("БОТ УСПІШНО ЗАПУЩЕНИЙ В РЕЖИМІ POLLING")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
