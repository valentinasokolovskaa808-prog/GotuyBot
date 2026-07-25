import os

# Автоматичне очищення токена від будь-яких випадкових пробілів
raw_token = os.getenv("BOT_TOKEN", "8891216844:AAEtznGW5kgTs1cnTbHisY0FlX9ojrMrqTc")
BOT_TOKEN = raw_token.strip().strip('"').strip("'").replace(" ", "").replace("\n", "").replace("\r", "")

# Telegram User ID адміністратора
ADMIN_IDS = [5270272994]
