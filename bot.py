import os
import logging
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardMarkup, KeyboardButton
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено в змінних оточення!")

ADMIN_ID = os.getenv("ADMIN_ID" =  5270272994)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

import database
database.init_db()


# --- Стан для FSM (Додавання рецепта) ---
class AddRecipeState(StatesGroup):
    waiting_for_title = State()
    waiting_for_ingredients = State()
    waiting_for_instructions = State()
    waiting_for_video_url = State()
    waiting_for_categories = State()


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
        [InlineKeyboardButton(text="➕ Додати рецепт", callback_data="admin_add_recipe")],
        [InlineKeyboardButton(text="📊 Статистика бази", callback_data="admin_stats")],
        [InlineKeyboardButton(text="🔄 Переініціалізувати базу", callback_data="admin_reinit")]
    ])

def get_category_choice_keyboard(selected_cats):
    """Клавіатура вибору категорій при додаванні"""
    def check(cat):
        return "✅ " if cat in selected_cats else ""

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{check('breakfast')}🍳 Сніданок", callback_data="toggle_breakfast"),
            InlineKeyboardButton(text=f"{check('lunch')}🥦 Обід", callback_data="toggle_lunch")
        ],
        [
            InlineKeyboardButton(text=f"{check('dinner')}🥦 Вечеря", callback_data="toggle_dinner"),
            InlineKeyboardButton(text=f"{check('baking')}🥐 Випічка", callback_data="toggle_baking")
        ],
        [
            InlineKeyboardButton(text=f"{check('desserts')}🍰 Десерт", callback_data="toggle_desserts")
        ],
        [
            InlineKeyboardButton(text="💾 Зберегти рецепт", callback_data="save_new_recipe")
        ]
    ])

def get_social_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 Telegram канал", url="https://t.me/gotuy_prosti_recepty")],
        [InlineKeyboardButton(text="🔹 TikTok", url="https://www.tiktok.com/@vitaly_is_cooking")],
        [InlineKeyboardButton(text="🔹 Instagram", url="https://www.instagram.com/vitaly_is_cooking/")],
        [InlineKeyboardButton(text="🔹 Facebook", url="https://www.facebook.com/GotuyProstiRecepty")]
    ])


# --- Відправка картки рецептів ---
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
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_reply_keyboard())


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


# --- Адмінська функціональність ---

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


@dp.callback_query(F.data == "admin_reinit")
async def process_admin_reinit(callback: types.CallbackQuery):
    await callback.answer()
    if os.path.exists("recipes.db"):
        os.remove("recipes.db")
    database.init_db()
    await callback.message.answer("✅ База даних успішно переініціалізована та оновлена!")


# --- Покрокове додавання рецепта (FSM) ---

@dp.callback_query(F.data == "admin_add_recipe")
async def start_add_recipe(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AddRecipeState.waiting_for_title)
    await callback.message.answer("📝 **Крок 1 з 5:** Введіть **назву рецепта** (наприклад: *Запіканка з сиром*):", parse_mode="Markdown")


@dp.message(AddRecipeState.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddRecipeState.waiting_for_ingredients)
    await message.answer("🛒 **Крок 2 з 5:** Введіть **інгредієнти** (або напишіть `-`, щоб пропустити):", parse_mode="Markdown")


@dp.message(AddRecipeState.waiting_for_ingredients)
async def process_ingredients(message: types.Message, state: FSMContext):
    text = message.text.strip()
    ingredients = "Рецепт та деталі у відео" if text == "-" else text
    await state.update_data(ingredients=ingredients)
    await state.set_state(AddRecipeState.waiting_for_instructions)
    await message.answer("👩‍🍳 **Крок 3 з 5:** Введіть **інструкцію приготування** (або напишіть `-`, щоб пропустити):", parse_mode="Markdown")


@dp.message(AddRecipeState.waiting_for_instructions)
async def process_instructions(message: types.Message, state: FSMContext):
    text = message.text.strip()
    instructions = "Дивіться відеорецепт у каналі" if text == "-" else text
    await state.update_data(instructions=instructions)
    await state.set_state(AddRecipeState.waiting_for_video_url)
    await message.answer("🔗 **Крок 4 з 5:** Введіть **посилання на відео/допис у Telegram** (або напишіть `-`, якщо немає):", parse_mode="Markdown")


@dp.message(AddRecipeState.waiting_for_video_url)
async def process_video_url(message: types.Message, state: FSMContext):
    text = message.text.strip()
    video_url = None if text == "-" else text
    await state.update_data(video_url=video_url, categories=[])
    await state.set_state(AddRecipeState.waiting_for_categories)
    
    await message.answer(
        "🏷 **Крок 5 з 5:** Оберіть **категорії** для рецепта (можна обрати декілька) та натисніть **Зберегти**:",
        parse_mode="Markdown",
        reply_markup=get_category_choice_keyboard([])
    )


@dp.callback_query(AddRecipeState.waiting_for_categories, F.data.startswith("toggle_"))
async def toggle_category(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.replace("toggle_", "")
    data = await state.get_data()
    categories = data.get("categories", [])

    if cat in categories:
        categories.remove(cat)
    else:
        categories.append(cat)

    await state.update_data(categories=categories)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=get_category_choice_keyboard(categories))


@dp.callback_query(AddRecipeState.waiting_for_categories, F.data == "save_new_recipe")
async def save_recipe(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    categories = data.get("categories", [])

    is_bf = 1 if "breakfast" in categories else 0
    is_ln = 1 if "lunch" in categories else 0
    is_dn = 1 if "dinner" in categories else 0
    is_bk = 1 if "baking" in categories else 0
    is_ds = 1 if "desserts" in categories else 0

    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recipes (title, ingredients, instructions, video_url, is_breakfast, is_lunch, is_dinner, is_baking, is_desserts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data["title"], data["ingredients"], data["instructions"], data["video_url"], is_bf, is_ln, is_dn, is_bk, is_ds))
    conn.commit()
    conn.close()

    await state.clear()
    await callback.message.answer(f"✅ Рецепт **«{data['title']}»** успішно збережено в базу даних!", parse_mode="Markdown")


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
