import os

# Отримуємо токен та автоматично видаляємо всі випадкові пробіли, переноси рядків або таби
RAW_TOKEN = os.getenv("BOT_TOKEN", "8005346082:AAGx52ien9wTW2vcSSA_mLBEaX-cPDBffPM")
BOT_TOKEN = RAW_TOKEN.strip()

ADMIN_IDS = [5270272994]
