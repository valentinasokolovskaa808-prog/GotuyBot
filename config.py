import os
import re

# Отримуємо значення з Environment Variable або вставленого рядка
RAW_TOKEN = os.getenv("BOT_TOKEN", "8005346082:AAGx52ien9wTW2vcSSA_mLBEaX-cPDBffPM")

# Жорстко очищаємо токен від усього зайвого (пробіли, лапки, переноси рядків)
BOT_TOKEN = re.sub(r'\s+', '', RAW_TOKEN).strip('"\'')

ADMIN_IDS = [5270272994]
