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
    """Создаем и запускаем бота"""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))

    logger.info("🤖 Бот успешно запущен и слушает команды...")

    # Запускаем бота
    await app.run_polling()

# Используем альтернативный способ запуска
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(main())  # Запускаем бота в виде фоновой задачи
    loop.run_forever()  # Держим event loop активным
