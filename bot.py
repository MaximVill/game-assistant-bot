import asyncio
from aiogram import Dispatcher, types, Bot, F
from aiogram.filters import Command

from config import BOT_TOKEN

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

@dp.message(F.text == 'Найти игру')
async def find_game_btn(message: types.Message):
    pass

@dp.message(F.text == 'Цены игр')
async def game_prices_btn(message: types.Message):
    pass

@dp.message(F.text == 'Раздачи')
async def distributions_btn(message: types.Message):
    pass

@dp.message(F.text == 'Новости')
async def news_btn(message: types.Message):
    pass

@dp.message(F.text == 'Помощь')
async def help_btn(message: types.Message):
    pass

async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())