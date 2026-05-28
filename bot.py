import asyncio
import os
import aiohttp
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN

from handlers import start, help, search, prices, giveaways, news
from services.rawg_service import RAWGService
from services.cheapshark_service import CheapSharkService
from services.freesteam_service import FreeSteamService
from services.stopgame_service import StopGameService
from utils.logger import LOGS_DIR

async def main():
    # Создаем директорию логов один раз при старте
    os.makedirs(LOGS_DIR, exist_ok=True)

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(search.router)
    dp.include_router(prices.router)
    dp.include_router(giveaways.router)
    dp.include_router(news.router)

    # Настраиваем единую сессию с таймаутом в 15 секунд
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Инициализируем сервисы с общей сессией
        rawg_service = RAWGService(session)
        cheapshark_service = CheapSharkService(session)
        freesteam_service = FreeSteamService(session)
        stopgame_service = StopGameService(session)

        # Кэшируем магазины при запуске
        await cheapshark_service.pre_fetch_stores()

        # Запускаем polling, передавая сервисы в качестве зависимостей в хендлеры
        await dp.start_polling(
            bot,
            rawg=rawg_service,
            cheapshark=cheapshark_service,
            freesteam=freesteam_service,
            stopgame=stopgame_service
        )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n[Info] Бот успешно остановлен.")