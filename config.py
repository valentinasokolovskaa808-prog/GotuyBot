import os

# Отримуємо токен та автоматично видаляємо всі випадкові пробіли, переноси рядків або таби
RAW_TOKEN = os.getenv("BOT_TOKEN", "8005346082:AAFNAIrcqqv9VvKr51SizaQJV1xXySMGS-U")
BOT_TOKEN = RAW_TOKEN.strip()

ADMIN_IDS = [5270272994]
