import logging
import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telethon import TelegramClient, events
import openai

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = os.getenv("OWNER_ID")  # ID владельца бота

if not all([TELEGRAM_BOT_TOKEN, API_ID, API_HASH, OPENAI_API_KEY, OWNER_ID]):
    raise ValueError("Не заданы переменные окружения!")

API_ID = int(API_ID)
OWNER_ID = int(OWNER_ID)

openai.api_key = OPENAI_API_KEY

CHANNELS_FILE = "channels.json"

client = TelegramClient("bot_session", API_ID, API_HASH)

try:
    with open(CHANNELS_FILE, "r") as file:
        channels = json.load(file)
except FileNotFoundError:
    channels = []

def save_channels():
    with open(CHANNELS_FILE, "w") as file:
        json.dump(channels, file)

# Функция для вывода списка каналов
async def canal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if channels:
        channel_list = "\n".join(channels)
        await update.message.reply_text(f"Мониторятся каналы:\n{channel_list}")
    else:
        await update.message.reply_text("Нет добавленных каналов.")

# Функция для добавления канала
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        channel = context.args[0]
        if channel not in channels:
            channels.append(channel)
            save_channels()
            await update.message.reply_text(f"Канал {channel} добавлен в мониторинг.")
        else:
            await update.message.reply_text("Этот канал уже добавлен.")
    else:
        await update.message.reply_text("Использование: /add @channel_username")

# Функция для удаления канала
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        channel = context.args[0]
        if channel in channels:
            channels.remove(channel)
            save_channels()
            await update.message.reply_text(f"Канал {channel} удалён из мониторинга.")
        else:
            await update.message.reply_text("Такого канала нет в списке.")
    else:
        await update.message.reply_text("Использование: /remove @channel_username")

# Обработчик сообщений из каналов
@client.on(events.NewMessage)
async def handler(event):
    if event.chat and event.chat.username in channels:
        keyboard = [
            [InlineKeyboardButton("✅ Опубликовать", callback_data="publish"),
             InlineKeyboardButton("❌ Не отправлять", callback_data="dismiss")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await app.bot.send_message(chat_id=OWNER_ID, text=event.message.message, reply_markup=markup)

# Обработчик кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "publish":
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Перефразируй это с добавлением смайликов: {query.message.text}"}]
        )
        new_text = response["choices"][0]["message"]["content"].strip()
        await context.bot.send_message(chat_id="@YOUR_CHANNEL", text=new_text)
        await query.edit_message_text("✅ Опубликовано!")
    elif query.data == "dismiss":
        await query.edit_message_text("❌ Не отправлено.")

# Основная функция
async def main():
    global app
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("canal", canal))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CallbackQueryHandler(button))

    asyncio.create_task(app.run_polling())
    await client.start()
    logger.info("Bot is running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(main())
    else:
        loop.run_until_complete(main())
