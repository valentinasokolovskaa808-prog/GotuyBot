from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Основне меню внизу чату
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍳 Сніданок"), KeyboardButton(text="🍲 Обід"), KeyboardButton(text="🥗 Вечеря")],
        [KeyboardButton(text="🥐 Випічка"), KeyboardButton(text="🍰 Десерти")],
        [KeyboardButton(text="🎬 Відео рецептів"), KeyboardButton(text="⭐ Нові рецепти")],
        [KeyboardButton(text="🎲 Випадковий рецепт"), KeyboardButton(text="🔍 Пошук рецепту")],
        [KeyboardButton(text="📲 Наші соцмережі"), KeyboardButton(text="✉️ Зв'язатися"), KeyboardButton(text="ℹ️ Про бота")]
    ],
    resize_keyboard=True
)
# Інлайн-кнопки з посиланнями під повідомленням
social_links_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📘 Facebook група", 
                url="https://www.facebook.com/GotuyProstiRecepty"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎵 TikTok", 
                url="https://www.tiktok.com/@vitaly_is_cooking?lang=ru-RU"
            )
        ],
        [
            InlineKeyboardButton(
                text="📸 Instagram", 
                url="https://www.instagram.com/vitaly_is_cooking/"
            )
        ]
    ]
)