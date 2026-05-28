from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from utils.logger import log_user_action

router = Router()

@router.message(Command('start'), StateFilter("*"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()  # Сбрасываем любое активное состояние
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
    await message.answer('Введите название существующей игры и мы расскажем всю информацию о ней.\n'
                         'Или же воспользуйся кнопками на клавиатуре для поиска и.т.д.', reply_markup=keyboard)
    await log_user_action(message.from_user.id, "Start Command", "/start", "Keyboard sent")