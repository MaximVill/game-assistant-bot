from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.cheapshark_service import CheapSharkService
from utils.logger import log_user_action

router = Router()
cheapshark = CheapSharkService()

# Состояния для поиска цен на игру
class PriceStates(StatesGroup):
    waiting_for_game_name = State()

# Обработчик кнопки 'Цены игр'
@router.message(F.text == 'Цены игр')
async def prices_start(message: types.Message, state: FSMContext):
    await message.answer('Введите название игры для сравнения цен:')
    await state.set_state(PriceStates.waiting_for_game_name)
    await log_user_action(message.from_user.id, "Start Price Search", "Button click: Цены игр", "User asked for game name")

# Обработчик ввода названия игры для поиска цен
@router.message(PriceStates.waiting_for_game_name)
async def prices_process(message: types.Message, state: FSMContext):
    query = message.text
    await message.answer(f'Ищу лучшие цены для "{query}"...')

    try:
        game_id = await cheapshark.find_game_id(query)
        await state.clear()

        if game_id:
            deals = await cheapshark.get_best_deals(game_id)
            if deals and "deals" in deals:
                best_deal = deals["deals"][0]
                store_id = best_deal["storeID"]
                price = best_deal["price"]

                # Упрощенное сопоставление магазинов (в реальном боте мы бы сопоставляли ID магазинов с названиями)
                response = f"Лучшая цена для {query}: {price}$\n"
                response += f"Магазин ID: {store_id}\n"
                response += f"Ссылка: {best_deal['url']}"

                await message.answer(response)
                await log_user_action(message.from_user.id, "Price Search", query, f"Found deal: {price}$")
            else:
                await message.answer('Цены на эту игру не найдены.')
                await log_user_action(message.from_user.id, "Price Search", query, "No deals found")
        else:
            await message.answer('Игра не найдена в базе CheapShark.')
            await log_user_action(message.from_user.id, "Price Search", query, "Game not found")
    except Exception as e:
        await message.answer('Произошла ошибка при поиске цен.')
        await log_user_action(message.from_user.id, "Price Search", query, "Error occurred", exception=e)
        await state.clear()
