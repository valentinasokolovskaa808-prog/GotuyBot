import os
import logging
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardMarkup, KeyboardButton
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено в змінних оточення!")

# Вкажіть ваш Telegram ID (або залиште None, якщо адмінка має бути доступна без обмежень)
# Наприклад: ADMIN_ID = 123456789
ADMIN_ID = os.getenv("ADMIN_ID", None)

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
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍳 Сніданок"), KeyboardButton(text="🥦 Обід"), KeyboardButton(text="🥦 Вечеря")],
            [KeyboardButton(text="🥐 Випічка"), KeyboardButton(text="🍰 Десерти")],
            [KeyboardButton(text="🎬 Відеорецепти"), KeyboardButton(text="🔎 Пошук рецепту")],
            [KeyboardButton(text="📲 Наші соцмережі")]
        ],
        resize_keyboard=True
    )

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика бази", callback_data="admin_stats")],
        [InlineKeyboardButton(text="🔄 Переініціалізувати базу", callback_data="admin_reinit")]
    ])

def get_social_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 Telegram канал", url="https://t.me/gotuy_prosti_recepty")],
        [InlineKeyboardButton(text="🔹 TikTok", url="https://www.tiktok.com/@vitaly_is_cooking")],
        [InlineKeyboardButton(text="🔹 Instagram", url="https://www.instagram.com/vitaly_is_cooking/")],
        [InlineKeyboardButton(text="🔹 Facebook", url="https://www.facebook.com/GotuyProstiRecepty")]
    ])


# --- Відправка картки кожного рецепта окремо ---
async def send_recipe_cards(message: types.Message, recipes: list, category_title: str = None):
    if not recipes:
        await message.answer(f"У категорії **{category_title}** поки немає рецептів 😔", parse_mode="Markdown")
        return

    if category_title:
        await message.answer(f"📋 **Знайдено рецепти ({len(recipes)}):**", parse_mode="Markdown")

    for r in recipes:
        title, ingredients, instructions, video_url = r
        
        text = f"🍳 **{title}**\n\n"
        
        if ingredients and ingredients != "Рецепт та деталі у відео":
            text += f"🛒 **Інгредієнти:**\n{ingredients}\n\n"
            
        if instructions and instructions != "Дивіться відеорецепт у каналі":
            text += f"👩‍🍳 **Приготування:**\n{instructions}\n\n"
            
        if video_url:
            text += f"🔗 [Дивитися відеорецепт]({video_url})"

        await message.answer(text, parse_mode="Markdown", disable_web_page_preview=False)
        await asyncio.sleep(0.3)


# --- Команди ---

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


@dp.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if ADMIN_ID and str(message.from_user.id) != str(ADMIN_ID):
        await message.answer("⛔ У вас немає доступу до панелі адміністратора.")
        return

    await message.answer(
        "⚙️ **Панель адміністратора**\n\nОберіть дію:",
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard()
    )


@dp.callback_query(F.data == "admin_stats")
async def process_admin_stats(callback: types.CallbackQuery):
    await callback.answer()
    
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM recipes")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_breakfast = 1")
    bf = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_lunch = 1")
    ln = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_dinner = 1")
    dn = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_baking = 1")
    bk = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_desserts = 1")
    ds = cursor.fetchone()[0]
    conn.close()

    stats_text = (
        f"📊 **Статистика бази даних:**\n\n"
        f"• Всього рецептів: **{total}**\n"
        f"• Сніданки: **{bf}**\n"
        f"• Обіди: **{ln}**\n"
        f"• Вечері: **{dn}**\n"
        f"• Випічка: **{bk}**\n"
        f"• Десерти: **{ds}**"
    )
    await callback.message.answer(stats_text, parse_mode="Markdown")


# --- Обробник текстових повідомлень ---

@dp.message()
async def main_handler(message: types.Message):
    text = message.text.strip() if message.text else ""
    if not text or text.startswith("/"):
        return

    text_lower = text.lower()

    if "сніданок" in text_lower:
        recipes = database.get_breakfast_recipes()
        await send_recipe_cards(message, recipes, "Сніданки")

    elif "обід" in text_lower:
        recipes = database.get_lunch_recipes()
        await send_recipe_cards(message, recipes, "Обіди")

    elif "вечеря" in text_lower:
        recipes = database.get_dinner_recipes()
        await send_recipe_cards(message, recipes, "Вечері")

    elif "випічка" in text_lower:
        recipes = database.get_baking_recipes()
        await send_recipe_cards(message, recipes, "Випічка")

    elif "десерт" in text_lower:
        recipes = database.get_dessert_recipes()
        await send_recipe_cards(message, recipes, "Десерти")

    elif "відеорецепти" in text_lower or "відео" in text_lower:
        recipes = database.get_video_recipes()
        await send_recipe_cards(message, recipes, "Відеорецепти")

    elif "пошук рецепту" in text_lower or "як шукати" in text_lower:
        await message.answer(
            "💡 **Як користуватися пошуком:**\n\n"
            "Просто напишіть у чат назву страви або інгредієнт:\n"
            "• `курка` — знайде страви з куркою\n"
            "• `салат` — знайде відповідні салати\n"
            "• `торт` — знайде торти та десерти",
            parse_mode="Markdown"
        )

    elif "соцмережі" in text_lower:
        await message.answer(
            "📲 **Наші офіційні сторінки та канали:**\n\n"
            "Переходьте за посиланнями нижче 👇",
            reply_markup=get_social_keyboard(),
            parse_mode="Markdown"
        )

    else:
        results = database.search_recipes(text)
        if results:
            await send_recipe_cards(message, results)
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
