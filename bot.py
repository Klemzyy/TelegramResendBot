import asyncio
import logging
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота (замени на свой)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"

# Обработчики команд
async def canal(update, context):
    await update.message.reply_text("Канал обработан!")

async def add(update, context):
    await update.message.reply_text("Добавлено!")

async def remove(update, context):
    await update.message.reply_text("Удалено!")

async def button(update, context):
    await update.callback_query.answer("Кнопка нажата!")

# Главная асинхронная функция
async def main():
    # Создание приложения Telegram бота
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавление обработчиков
    app.add_handler(CommandHandler("canal", canal))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CallbackQueryHandler(button))

    logger.info("🤖 Бот успешно запущен и слушает команды...")

    # Запуск бота в режиме опроса
    await app.run_polling()

# Точка входа
if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())  # Корректный запуск event loop
