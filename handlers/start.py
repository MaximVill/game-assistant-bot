from aiogram import Router, types, F
from aiogram.filters import Command

router = Router()

# Обработчик команды /start
@router.message(Command('start'))
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
