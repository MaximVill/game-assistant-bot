from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.rawg_service import RAWGService
from utils.logger import log_user_action

router = Router()
rawg = RAWGService()

# Состояния для поиска игры
class SearchStates(StatesGroup):
    waiting_for_game_name = State()

# Обработчик кнопки 'Найти игру'
@router.message(F.text == 'Найти игру')
async def find_game_start(message: types.Message, state: FSMContext):
    await message.answer('Введите название игры, которую хотите найти:')
    await state.set_state(SearchStates.waiting_for_game_name)
    await log_user_action(message.from_user.id, "Start Search", "Button click: Найти игру", "User asked for game name")

# Обработчик ввода названия игры для поиска
@router.message(SearchStates.waiting_for_game_name)
async def find_game_process(message: types.Message, state: FSMContext):
    query = message.text
    await message.answer(f'Ищу игру "{query}"...')

    try:
        results = await rawg.search_game(query)
        await state.clear()

        if results:
            response = "Вот что я нашел:\n\n"
            for game in results:
                name = game.get("name")
                rating = game.get("rating", "Нет рейтинга")
                game_id = game.get("id")
                response += f"{name} | Рейтинг: {rating} (ID: {game_id})\n"

            await message.answer(response)
            await log_user_action(message.from_user.id, "Game Search", query, f"Found {len(results)} games")
        else:
            await message.answer('К сожалению, ничего не нашлось.')
            await log_user_action(message.from_user.id, "Game Search", query, "No results found")
    except Exception as e:
        await message.answer('Произошла ошибка при поиске игры.')
        await log_user_action(message.from_user.id, "Game Search", query, "Error occurred", exception=e)
        await state.clear()
