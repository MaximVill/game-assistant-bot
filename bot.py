import os
import asyncio
from aiogram import Dispatcher, types, Bot
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

@dp.message(Command('start'))
async def start(message: types.Message):
    buttons = [
        [
            types.KeyboardButton(text='Найти игру'),
            types.KeyboardButton(text='Цены игр')
        ],
        [
            types.KeyboardButton(text='Раздачи'),
            types.KeyboardButton(text='Новости')
        ],
        [types.KeyboardButton(text='Помощь')]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer('Воспользуйся кнопками на клавиатуре для поиска информации.', reply_markup=keyboard)

async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())