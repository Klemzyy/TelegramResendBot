import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Я ваш бот.")

async def main():
    """Создаем и запускаем бота без конфликта с event loop"""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))

    logger.info("🤖 Бот успешно запущен и слушает команды...")

    # Запускаем бота
    await app.run_polling()

# Проверяем, есть ли активный event loop
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())  # Если event loop уже запущен, создаём задачу
except RuntimeError:
    asyncio.run(main())  # Если event loop нет, запускаем стандартно
