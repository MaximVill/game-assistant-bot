from aiogram import Router, types, F

router = Router()

# Обработчик кнопки 'Помощь'
@router.message(F.text == 'Помощь')
async def help_handler(message: types.Message):
    help_text = (
        "Я — игровой ассистент. Чем я могу помочь?\n\n"
        "Найти игру — поиск информации об играх через RAWG API\n"
        "Цены игр — поиск лучших предложений через CheapShark\n"
        "Раздачи — актуальные бесплатные игры с FreeSteam\n"
        "Новости — последние новости из мира игр с StopGame"
    )
    await message.answer(help_text)
