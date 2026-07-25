from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Головне меню з кнопками
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🍳 Сніданок"),
            KeyboardButton(text="🍲 Обід"),
            KeyboardButton(text="🥗 Вечеря")
        ],
        [
            KeyboardButton(text="🥐 Випічка"),
            KeyboardButton(text="🍰 Десерти")
        ],
        [
            KeyboardButton(text="🎬 Відеорецепти"),
            KeyboardButton(text="🔎 Пошук рецепту")
        ],
        [
            KeyboardButton(text="📲 Наші соцмережі")
        ]
    ],
    resize_keyboard=True
)

# Меню з посиланнями на соцмережі
social_links_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✈️ Telegram канал", url="https://t.me/gotuy_prosti_recepty"),
            InlineKeyboardButton(text="🎵 TikTok", url="https://www.tiktok.com/@gotuy_prosti_recepty")
        ],
        [
            InlineKeyboardButton(text="📷 Instagram", url="https://www.instagram.com/gotuy_prosti_recepty"),
            InlineKeyboardButton(text="📘 Facebook", url="https://www.facebook.com/gotuy.prosti.recepty")
        ]
    ]
)
