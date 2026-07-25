import os

# Отримуємо токен і примусово видаляємо всі пробіли, кавички та переноси
raw_token = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_ЯКЩО_НЕМАЄ_В_ENV")
BOT_TOKEN = raw_token.strip().strip('"').strip("'").replace(" ", "").replace("\n", "").replace("\r", "")

# Telegram User ID адміністратора
ADMIN_IDS = [5270272994]
