from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from utils.logger import log_user_action

router = Router()

@router.message(F.text == 'Помощь', StateFilter("*"))
async def help_handler(message: types.Message, state: FSMContext):
    await state.clear()  # Выводим пользователя из тупика FSM
    help_text = (
        "Я — игровой ассистент. Чем я могу помочь?\n\n"
        "Найти игру — поиск информации об играх через RAWG API\n"
        "Цены игр — поиск лучших предложений через CheapShark\n"
        "Раздачи — актуальные бесплатные игры с FreeSteam\n"
        "Новости — последние новости из мира игр с StopGame"
    )
    await message.answer(help_text)
    await log_user_action(message.from_user.id, "Help Command", "Button click: Помощь", "Help text sent")