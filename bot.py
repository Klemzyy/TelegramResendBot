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
    """Основная асинхронная функция запуска бота"""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))

    logger.info("🤖 Бот успешно запущен и слушает команды...")
    
    # Запускаем бота без создания нового event loop
    await app.run_polling()

# Проверяем, запущен ли event loop
if __name__ == "__main__":
    try:
        asyncio.run(main())  # Запуск бота
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.create_task(main())  # Запускаем бота в текущем event loop
