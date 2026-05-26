import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Токен бота Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
# API ключ для RAWG
RAWG_API_KEY = os.getenv("RAWG_API_KEY")

# Базовые URL для API сервисов
RAWG_BASE_URL = "https://api.rawg.io/api"
CHEAPSHARK_BASE_URL = "https://www.cheapshark.com/api/1.0"
