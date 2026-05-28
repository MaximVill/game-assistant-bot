from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from services.cheapshark_service import CheapSharkService
from utils.logger import log_user_action

router = Router()

class PriceStates(StatesGroup):
    waiting_for_game_name = State()
    viewing_deals = State()

async def build_price_message(query: str, game_id: str, cheapshark: CheapSharkService, sort_by: str = "price"):
    deals_data = await cheapshark.get_best_deals(game_id)
    # Используем данные о магазинах из кэша сервиса
    stores = cheapshark.stores_cache

    if not deals_data or "deals" not in deals_data:
        return "Цены на эту игру не найдены.", None

    deals = deals_data["deals"]

    if sort_by == "price":
        deals.sort(key=lambda x: float(x['price']))
    elif sort_by == "savings":
        deals.sort(key=lambda x: float(x['savings']), reverse=True)

    response = f"Цены для <b>{query}</b>:\n\n"
    for deal in deals[:10]:
        store_name = stores.get(deal['storeID'], f"Store {deal['storeID']}")
        price = deal['price']
        savings = float(deal['savings'])
        url = f"https://www.cheapshark.com/redirect?dealID={deal['dealID']}"
        response += f"<a href='{url}'>{store_name}</a>: {price}$ (Скидка: {savings:.0f}%)\n"

    builder = InlineKeyboardBuilder()
    builder.button(text="Сначала дешевые", callback_data=f"sort_price_{game_id}")
    builder.button(text="По размеру скидки", callback_data=f"sort_savings_{game_id}")

    return response, builder.as_markup()

@router.message(F.text == 'Цены игр', StateFilter("*"))
async def prices_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('Введите название игры для сравнения цен:')
    await state.set_state(PriceStates.waiting_for_game_name)
    await log_user_action(message.from_user.id, "Start Price Search", "Button click: Цены игр", "User asked for game name")

@router.message(PriceStates.waiting_for_game_name)
async def prices_process(message: types.Message, state: FSMContext, cheapshark: CheapSharkService):
    query = message.text
    await message.answer(f'Ищу лучшие цены для "{query}"...')

    try:
        game_id = await cheapshark.find_game_id(query)
        if game_id:
            await state.set_state(PriceStates.viewing_deals)
            await state.update_data(current_game_id=game_id, current_game_query=query)

            text, markup = await build_price_message(query, game_id, cheapshark, "price")
            await message.answer(text, reply_markup=markup)
            await log_user_action(message.from_user.id, "Price Search", query, f"Found deals for game {game_id}")
        else:
            await message.answer('Игра не найдена в базе CheapShark.')
            await log_user_action(message.from_user.id, "Price Search", query, "Game not found")
            await state.clear()
    except Exception as e:
        await message.answer('Произошла ошибка при поиске цен.')
        await log_user_action(message.from_user.id, "Price Search", query, "Error occurred", exception=e)
        await state.clear()

@router.callback_query(F.data.startswith("sort_"))
async def prices_sort_callback(callback: types.CallbackQuery, state: FSMContext, cheapshark: CheapSharkService):
    data = callback.data.split("_")
    sort_type = data[1]
    game_id = data[2]

    user_data = await state.get_data()
    query = user_data.get("current_game_query", "игра")

    try:
        text, markup = await build_price_message(query, game_id, cheapshark, sort_type)
        try:
            await callback.message.edit_text(text, reply_markup=markup)
            await callback.answer(f"Отсортировано по: {'цене' if sort_type == 'price' else 'скидке'}")
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                await callback.answer("Уже отсортировано.")
            else:
                raise e
        await log_user_action(callback.from_user.id, "Price Sort", query, f"Sorted by {sort_type}")
    except Exception as e:
        await callback.answer("Ошибка при обновлении списка.")
        await log_user_action(callback.from_user.id, "Price Sort", query, "Error occurred", exception=e)