from aiogram import Router, types, F
from services.stopgame_service import StopGameService
from utils.logger import log_user_action

router = Router()
stopgame = StopGameService()

# Обработчик кнопки 'Новости'
@router.message(F.text == 'Новости')
async def news_handler(message: types.Message):
    await message.answer('Загружаю последние новости...')

    try:
        news_items = await stopgame.get_latest_news()

        if news_items:
            response = "Последние новости индустрии:\n\n"
            for item in news_items:
                response += f"{item['title']}\n{item['link']}\n\n"

            await message.answer(response)
            await log_user_action(message.from_user.id, "Get News", "Button click: Новости", f"Found {len(news_items)} news items")
        else:
            await message.answer('Новости на данный момент недоступны.')
            await log_user_action(message.from_user.id, "Get News", "Button click: Новости", "No news found")
    except Exception as e:
        await message.answer('Произошла ошибка при загрузке новостей.')
        await log_user_action(message.from_user.id, "Get News", "Button click: Новости", "Error occurred", exception=e)
