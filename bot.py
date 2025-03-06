import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.executor import start_webhook
import openai

# Загружаем переменные окружения
TOKEN = os.getenv("TOKEN")  # Твой Telegram токен
GPT_API_KEY = os.getenv("GPT_API_KEY")  # API ключ OpenAI
OWNER_ID = int(os.getenv("OWNER_ID"))  # Твой Telegram ID
POST_CHANNEL_ID = os.getenv("POST_CHANNEL_ID")  # Канал для публикации

# Webhook настройки для Render
WEBHOOK_HOST = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
PORT = int(os.getenv("PORT", 5000))

# Настройки бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
openai.api_key = GPT_API_KEY

# Хранение каналов
channels = set()
publish_channel = POST_CHANNEL_ID  # Канал для публикации

# Команда /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я бот для мониторинга каналов. Используйте /add, /remove, /channels, /resend.")

# Команда /add (добавить канал)
@dp.message_handler(commands=["add"])
async def add_channel(message: types.Message):
    if message.chat.id != OWNER_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /add @channel_username")
        return
    channels.add(args[1])
    await message.answer(f"Канал {args[1]} добавлен!")

# Команда /remove (удалить канал)
@dp.message_handler(commands=["remove"])
async def remove_channel(message: types.Message):
    if message.chat.id != OWNER_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /remove @channel_username")
        return
    channels.discard(args[1])
    await message.answer(f"Канал {args[1]} удален!")

# Команда /channels (показать добавленные каналы)
@dp.message_handler(commands=["channels"])
async def list_channels(message: types.Message):
    if message.chat.id != OWNER_ID:
        return
    if not channels:
        await message.answer("Список каналов пуст.")
    else:
        await message.answer("Мониторятся каналы:\n" + "\n".join(channels))

# Команда /resend (изменить канал для публикации)
@dp.message_handler(commands=["resend"])
async def change_publish_channel(message: types.Message):
    if message.chat.id != OWNER_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /resend @your_channel")
        return
    global publish_channel
    publish_channel = args[1]
    await message.answer(f"Теперь посты публикуются в {publish_channel}")

# Обработчик новых сообщений в отслеживаемых каналах
@dp.channel_post_handler()
async def new_post_handler(message: types.Message):
    if message.chat.username not in channels:
        return
    
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Опубликовать", callback_data=f"publish_{message.message_id}"),
        InlineKeyboardButton("❌ Не публиковать", callback_data="dismiss")
    )
    await bot.send_message(OWNER_ID, f"Новый пост из {message.chat.title}:", reply_markup=keyboard)

# Обработчик нажатий на кнопки
@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    if callback.data.startswith("publish_"):
        message_id = callback.data.split("_")[1]
        original_message = await bot.forward_message(OWNER_ID, callback.message.chat.id, message_id)
        new_text = await rewrite_post(original_message.text)
        await bot.send_message(publish_channel, new_text)
        await callback.answer("✅ Пост опубликован!")
    elif callback.data == "dismiss":
        await callback.answer("❌ Пост отклонен!")

# Функция обработки текста через ChatGPT
async def rewrite_post(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Перефразируй сообщение, добавив немного эмодзи"},
                  {"role": "user", "content": text}]
    )
    return response["choices"][0]["message"]["content"]

# Запуск бота через Webhook
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info("🚀 Бот запущен через Webhook")

async def on_shutdown(dp):
    await bot.delete_webhook()

start_webhook(
    dispatcher=dp,
    webhook_path=WEBHOOK_PATH,
    on_startup=on_startup,
    on_shutdown=on_shutdown,
    skip_updates=True,
    host="0.0.0.0",
    port=PORT
)
