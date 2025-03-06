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
    """Запускаем бота без создания нового event loop"""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))

    logger.info("🤖 Бот успешно запущен и слушает команды...")
    
    # Запускаем polling в уже существующем event loop
    await app.run_polling()

# Главный блок
if __name__ == "__main__":
    if asyncio.get_event_loop().is_running():
        asyncio.create_task(main())  # Если event loop уже запущен, создаём задачу
    else:
        asyncio.run(main())  # Если нет, запускаем стандартно
