import asyncio
from aiogram import Dispatcher, Bot
from config import BOT_TOKEN

from handlers import start, help, search, prices, giveaways, news

# Основная функция запуска бота
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(search.router)
    dp.include_router(prices.router)
    dp.include_router(giveaways.router)
    dp.include_router(news.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
