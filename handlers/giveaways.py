from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from services.freesteam_service import FreeSteamService
from utils.logger import log_user_action

router = Router()

@router.message(F.text == 'Раздачи', StateFilter("*"))
async def giveaways_handler(message: types.Message, state: FSMContext, freesteam: FreeSteamService):
    await state.clear()
    await message.answer('Загружаю актуальные раздачи...')

    try:
        giveaways = await freesteam.get_giveaways()

        if giveaways:
            response = "Актуальные бесплатные игры:\n\n"
            for g in giveaways:
                response += f"{g['title']}\n{g['link']}\n\n"

            await message.answer(response)
            await log_user_action(message.from_user.id, "Get Giveaways", "Button click: Раздачи", f"Found {len(giveaways)} giveaways")
        else:
            await message.answer('На данный момент раздач не найдено.')
            await log_user_action(message.from_user.id, "Get Giveaways", "Button click: Раздачи", "No giveaways found")
    except Exception as e:
        await message.answer('Произошла ошибка при загрузке раздач.')
        await log_user_action(message.from_user.id, "Get Giveaways", "Button click: Раздачи", "Error occurred", exception=e)