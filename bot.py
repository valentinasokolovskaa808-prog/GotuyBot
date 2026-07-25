import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from config import BOT_TOKEN, ADMIN_IDS

# Вмикаємо детальні логи в консоль Render
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Ініціалізація бота та диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хендлер для команды /start
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    logger.info(f"Отримано /start від користувача: {message.from_user.id}")
    await message.answer("Привіт! Бот працює та готовий до використання.")

# Хендлер для команды /admin
@dp.message(Command("admin"))
async def admin_handler(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Панель адміністратора активна.")
    else:
        await message.answer("У вас немає доступу до цієї команди.")

# Логування будь-яких інших текстових повідомлень
@dp.message()
async def echo_handler(message: types.Message):
    logger.info(f"Отримано повідомлення: '{message.text}' від {message.from_user.id}")
    await message.answer(f"Ви написали: {message.text}")

async def main():
    # 1. Видаляємо вебхуки та очищаємо накопичені старі повідомлення
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("=" * 50)
    logger.info("БОТ УСПІШНО ЗАПУЩЕНИЙ ТА ГОТОВИЙ ДО РОБОТИ")
    logger.info("=" * 50)
    
    # 2. Запускаємо polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот зупинений.")
