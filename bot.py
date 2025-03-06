import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from openai import AsyncOpenAI

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
GPT_API_KEY = "YOUR_OPENAI_API_KEY"
OWNER_ID = YOUR_TELEGRAM_ID  # Замени на свой Telegram ID
POST_CHANNEL_ID = "@your_post_channel"  # Канал для публикации
db_channels = set()  # Храним ID каналов для мониторинга

bot = Bot(token=TOKEN)
dp = Dispatcher()
gpt_client = AsyncOpenAI(api_key=GPT_API_KEY)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def rephrase_text(text):
    """ Перефразирование текста с помощью GPT. """
    response = await gpt_client.completions.create(
        model="gpt-4",
        prompt=f"Перефразируй и добавь эмодзи: {text}",
        max_tokens=200
    )
    return response.choices[0].text.strip()

@dp.message(Command("add"))
async def add_channel(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("⛔ У вас нет прав на это действие.")
    
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❌ Укажите ID или @юзернейм канала.")
    
    channel_id = args[1]
    db_channels.add(channel_id)
    await message.reply(f"✅ Канал {channel_id} добавлен в мониторинг!")

@dp.message(Command("remove"))
async def remove_channel(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("⛔ У вас нет прав на это действие.")
    
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❌ Укажите ID или @юзернейм канала.")
    
    channel_id = args[1]
    if channel_id in db_channels:
        db_channels.remove(channel_id)
        await message.reply(f"🗑 Канал {channel_id} удалён из мониторинга!")
    else:
        await message.reply("❌ Такого канала нет в списке.")

@dp.message(Command("channel"))
async def list_channels(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("⛔ У вас нет прав на это действие.")
    
    if not db_channels:
        await message.reply("📭 Список отслеживаемых каналов пуст.")
    else:
        channels_list = "\n".join(db_channels)
        await message.reply(f"📡 Отслеживаемые каналы:\n{channels_list}")

@dp.message(Command("resend"))
async def change_post_channel(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("⛔ У вас нет прав на это действие.")
    
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❌ Укажите новый канал для публикаций.")
    
    global POST_CHANNEL_ID
    POST_CHANNEL_ID = args[1]
    await message.reply(f"✅ Теперь посты будут публиковаться в {POST_CHANNEL_ID}")

async def handle_new_post(post):
    """ Обработчик новых постов из каналов. """
    text = post.text or post.caption or "Без текста"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"approve_{post.message_id}")],
        [InlineKeyboardButton(text="❌ Не публиковать", callback_data="decline")]
    ])
    
    await bot.send_message(OWNER_ID, f"📩 Новый пост:\n\n{text}", reply_markup=keyboard)

@dp.callback_query()
async def handle_callback(call: types.CallbackQuery):
    if call.data.startswith("approve_"):
        post_id = call.data.split("_")[1]
        
        message = await bot.forward_message(OWNER_ID, POST_CHANNEL_ID, post_id)
        rephrased_text = await rephrase_text(message.text)
        
        await bot.send_message(POST_CHANNEL_ID, f"✨ {rephrased_text}")
        await call.message.edit_text("✅ Пост опубликован!")

    elif call.data == "decline":
        await call.message.edit_text("❌ Пост не опубликован.")

async def main():
    logger.info("🤖 Бот запущен и слушает команды...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
