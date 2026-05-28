import html
import re
import traceback
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from services.rawg_service import RAWGService
from services.cheapshark_service import CheapSharkService
from utils.logger import log_user_action

# Импортируем состояния цен для исключения конфликтов
from handlers.prices import PriceStates

router = Router()


class SearchStates(StatesGroup):
    waiting_for_game_name = State()


def clean_html(raw_html: str) -> str:
    """Очищает строку от HTML тегов."""
    clean_re = re.compile('<.*?>')
    return re.sub(clean_re, '', raw_html)


@router.message(F.text == 'Найти игру', StateFilter("*"))
async def find_game_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('Введите название игры, которую хотите найти:')
    await state.set_state(SearchStates.waiting_for_game_name)
    await log_user_action(message.from_user.id, "Start Search", "Button click: Найти игру", "User asked for game name")


@router.message(SearchStates.waiting_for_game_name)
async def find_game_process(message: types.Message, state: FSMContext, rawg: RAWGService):
    query = message.text
    await message.answer(f'Ищу игру "{query}"...')

    try:
        results = await rawg.search_game(query)
        await state.clear()

        if results:
            response = "Вот что я нашел:\n\n"
            for i, game in enumerate(results, 1):
                name = html.escape(game.get("name", "Неизвестно"))
                rating = game.get("rating", "Нет рейтинга")
                response += f"{i}. <code>{name}</code> | Рейтинг: {rating}\n"

            await message.answer(response)
            await log_user_action(message.from_user.id, "Game Search", query, f"Found {len(results)} games")
        else:
            await message.answer('К сожалению, ничего не нашлось.')
            await log_user_action(message.from_user.id, "Game Search", query, "No results found")
    except Exception as e:
        await message.answer('Произошла ошибка при поиске игры.')
        await log_user_action(message.from_user.id, "Game Search", query, "Error occurred", exception=e)
        await state.clear()


# Обработчик принимает любой ввод, кроме тех состояний, которые ожидают конкретного ввода названия.
@router.message(
    ~StateFilter(PriceStates.waiting_for_game_name, SearchStates.waiting_for_game_name),
    F.text & ~F.text.startswith('/') & ~F.text.in_({'Найти игру', 'Цены игр', 'Раздачи', 'Новости', 'Помощь'})
)
async def direct_search_handler(message: types.Message, state: FSMContext, rawg: RAWGService,
                                cheapshark: CheapSharkService):
    query = message.text

    # Сбрасываем предыдущие пассивные состояния (например, просмотр цен), так как начался новый поиск
    await state.clear()

    await message.answer(f'Ищу информацию об игре "{query}"...')

    try:
        # 1. Поиск игры в RAWG
        search_results = await rawg.search_game(query)
        if not search_results:
            await message.answer('Игра не найдена.')
            await log_user_action(message.from_user.id, "Direct Search", query, "Game not found")
            return

        game_id = search_results[0]['id']
        game_details = await rawg.get_game_details(game_id)

        if not game_details:
            await message.answer('Не удалось получить детали игры.')
            return

        # 2. Поиск цены в CheapShark
        price_info = "Цена в магазинах: не найдена"
        try:
            cs_id = await cheapshark.find_game_id(game_details.get('name', ''))
            if cs_id:
                deals_data = await cheapshark.get_best_deals(cs_id)
                if deals_data and isinstance(deals_data, dict) and "deals" in deals_data and deals_data["deals"]:
                    best_deal = deals_data["deals"][0]
                    store_name = cheapshark.stores_cache.get(best_deal['storeID'], "Магазин")
                    price_info = f"Лучшая цена: <b>{best_deal['price']}$</b> ({store_name})"
        except Exception as cs_err:
            print(f"[Warning] Ошибка поиска цен в CheapShark: {cs_err}")
            price_info = "Цена временно недоступна (ошибка API цен)"

        # 3. Формирование полей карточки
        name = html.escape(game_details.get('name', 'Неизвестно'))

        # Очистка и строгое ограничение длины описания
        raw_desc = game_details.get('description_raw') or game_details.get('description') or 'Описание отсутствует'
        cleaned_desc = clean_html(raw_desc)
        if len(cleaned_desc) > 300:
            cleaned_desc = cleaned_desc[:297] + "..."
        desc = html.escape(cleaned_desc)

        rating = game_details.get('rating', 'Нет рейтинга')
        released = game_details.get('released', 'Неизвестна')

        platforms_list = [p['platform']['name'] for p in game_details.get('platforms', []) if 'platform' in p]
        platforms = ", ".join(platforms_list) if platforms_list else "Не указаны"
        platforms = html.escape(platforms)

        website_url = game_details.get('website')
        if website_url and website_url.startswith("http"):
            website_link = f"<a href='{html.escape(website_url)}'>ссылка</a>"
        else:
            website_link = "Нет ссылки"

        # Безопасный парсинг системных требований
        reqs = "Не указаны"
        for p in game_details.get('platforms', []):
            if p.get('platform', {}).get('slug') == 'pc':
                reqs_dict = p.get('requirements_en') or p.get('requirements_ru') or p.get('requirements')
                if isinstance(reqs_dict, dict):
                    min_req = reqs_dict.get('minimum')
                    rec_req = reqs_dict.get('recommended')
                    if min_req and rec_req:
                        reqs = f"{min_req}\n\n{rec_req}"
                    elif min_req:
                        reqs = min_req
                    elif rec_req:
                        reqs = rec_req
                elif isinstance(reqs_dict, str):
                    reqs = reqs_dict
                break

        # Очистка и строгое ограничение длины системных требований
        reqs = clean_html(reqs)
        if len(reqs) > 300:
            reqs = reqs[:297] + "..."
        reqs = html.escape(reqs)

        # Сборка финального сообщения (гарантированно менее 1024 символов)
        caption = (
            f"<b>{name}</b>\n\n"
            f"Рейтинг: {rating}\n"
            f"Дата выхода: {released}\n"
            f"Платформы: {platforms}\n"
            f"{price_info}\n\n"
            f"<b>Описание:</b>\n{desc}\n\n"
            f"Официальный сайт: {website_link}\n\n"
            f"<b>Системные требования:</b>\n{reqs}"
        )

        # 4. Отправка
        image_url = game_details.get('background_image')
        if image_url:
            try:
                await message.answer_photo(image_url, caption=caption)
            except Exception as img_err:
                print(f"[Warning] Не удалось отправить фото игры: {img_err}")
                await message.answer(caption)
        else:
            await message.answer(caption)

        await log_user_action(message.from_user.id, "Direct Search Card", query, "Card sent")

    except Exception as e:
        print("[Error] Критическая ошибка в direct_search_handler:")
        traceback.print_exc()
        await message.answer('Произошла ошибка при создании карточки игры.')
        await log_user_action(message.from_user.id, "Direct Search Card", query, "Error occurred", exception=e)