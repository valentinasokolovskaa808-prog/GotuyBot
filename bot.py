import os
import logging
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено в змінних оточення!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

import database
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
        return

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()


# --- Клавіатури ---
def get_main_reply_keyboard():
    """Нижня текстова клавіатура"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍳 Сніданок"), KeyboardButton(text="🥦 Обід"), KeyboardButton(text="🥦 Вечеря")],
            [KeyboardButton(text="🥐 Випічка"), KeyboardButton(text="🍰 Десерти")],
            [KeyboardButton(text="🎬 Відеорецепти"), KeyboardButton(text="🔎 Пошук рецепту")],
            [KeyboardButton(text="📲 Наші соцмережі")]
        ],
        resize_keyboard=True
    )

def get_social_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 Telegram канал", url="https://t.me/gotuy_prosti_recepty")],
        [InlineKeyboardButton(text="🔹 TikTok", url="https://www.tiktok.com/@vitaly_is_cooking")],
        [InlineKeyboardButton(text="🔹 Instagram", url="https://www.instagram.com/vitaly_is_cooking/")],
        [InlineKeyboardButton(text="🔹 Facebook", url="https://www.facebook.com/GotuyProstiRecepty")]
    ])


def format_recipe_list(recipes, title):
    if not recipes:
        return f"У категорії **{title}** поки немає рецептів."

    text = f"📋 **Категорія: {title}** ({len(recipes)})\n\n"
    for r in recipes:
        recipe_title, ingredients, instructions, video_url = r
        text += f"🔹 **{recipe_title}**\n"
        if video_url:
            text += f"🔗 [Дивитися відеорецепт]({video_url})\n"
        text += "───────────────\n"
    return text


# --- Обробники команд ---

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    welcome_text = (
        f"Привіт, {message.from_user.first_name}! 👋\n\n"
        f"Ласкаво просимо до бота каналу **«Готуй! Прості рецепти»**! 🍳\n\n"
        f"Обирайте категорію в меню нижче або просто напишіть назву страви для пошуку:"
    )
    await message.answer(
        welcome_text, parse_mode="Markdown", reply_markup=get_main_reply_keyboard()
    )


# --- Обробник усіх текстових повідомлень та кнопок ---

@dp.message()
async def main_handler(message: types.Message):
    text = message.text.strip() if message.text else ""
    if not text or text.startswith("/"):
        return

    text_lower = text.lower()

    # 1. Сніданок
    if "сніданок" in text_lower:
        recipes = database.get_breakfast_recipes()
        msg_text = format_recipe_list(recipes, "Сніданки")
        await message.answer(msg_text, parse_mode="Markdown", disable_web_page_preview=True)

    # 2. Обід
    elif "обід" in text_lower:
        recipes = database.get_lunch_recipes()
        msg_text = format_recipe_list(recipes, "Обіди")
        await message.answer(msg_text, parse_mode="Markdown", disable_web_page_preview=True)

    # 3. Вечеря
    elif "вечеря" in text_lower:
        recipes = database.get_dinner_recipes()
        msg_text = format_recipe_list(recipes, "Вечері")
        await message.answer(msg_text, parse_mode="Markdown", disable_web_page_preview=True)

    # 4. Випічка
    elif "випічка" in text_lower:
        recipes = database.get_baking_recipes()
        msg_text = format_recipe_list(recipes, "Випічка")
        await message.answer(msg_text, parse_mode="Markdown", disable_web_page_preview=True)

    # 5. Десерти
    elif "десерт" in text_lower:
        recipes = database.get_dessert_recipes()
        msg_text = format_recipe_list(recipes, "Десерти")
        await message.answer(msg_text, parse_mode="Markdown", disable_web_page_preview=True)

    # 6. Відеорецепти
    elif "відеорецепти" in text_lower or "відео" in text_lower:
        recipes = database.get_video_recipes()
        msg_text = format_recipe_list(recipes, "Відеорецепти")
        await message.answer(msg_text, parse_mode="Markdown", disable_web_page_preview=True)

    # 7. Як шукати / Пошук рецепту
    elif "пошук рецепту" in text_lower or "як шукати" in text_lower:
        await message.answer(
            "💡 **Як користуватися пошуком:**\n\n"
            "Просто напишіть у чат назву страви або інгредієнт:\n"
            "• `курка` — знайде страви з куркою\n"
            "• `салат` — знайде відповідні салати\n"
            "• `торт` — знайде торти та десерти",
            parse_mode="Markdown"
        )

    # 8. Наші соцмережі
    elif "соцмережі" in text_lower:
        await message.answer(
            "📲 **Наші офіційні сторінки та канали:**\n\n"
            "Переходьте за посиланнями нижче 👇",
            reply_markup=get_social_keyboard(),
            parse_mode="Markdown"
        )

    # 9. Текстовий пошук за назвою чи інгредієнтом
    else:
        results = database.search_recipes(text)
        if results:
            msg_text = f"🔎 **Результати пошуку за запитом «{text}» ({len(results)}):**\n\n"
            for r in results:
                recipe_title, ingredients, instructions, video_url = r
                msg_text += f"🔹 **{recipe_title}**\n"
                if video_url:
                    msg_text += f"🔗 [Дивитися відеорецепт]({video_url})\n"
                msg_text += "───────────────\n"
            await message.answer(msg_text, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await message.answer(
                f"За запитом **«{text}»** нічого не знайдено 😔\n\n"
                f"Спробуйте ввести інше слово (наприклад: *салат*, *сир*, *курка*).",
                parse_mode="Markdown"
            )


# --- Запуск бота ---
async def main():
    server_thread = Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    logging.info("БОТ УСПІШНО ЗАПУЩЕНИЙ В РЕЖИМІ POLLING")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
