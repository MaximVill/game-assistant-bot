import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Токен бота Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
# API ключ для RAWG
RAWG_API_KEY = os.getenv("RAWG_API_KEY")

# Базовая проверка конфигурации перед запуском
if not BOT_TOKEN:
    print("[Error] BOT_TOKEN отсутствует в переменных окружения или файле .env")
    sys.exit(1)

if not RAWG_API_KEY:
    print("[Warning] RAWG_API_KEY отсутствует. Поиск игр через RAWG работать не будет.")

# Базовые URL для API сервисов
RAWG_BASE_URL = "https://api.rawg.io/api"
CHEAPSHARK_BASE_URL = "https://www.cheapshark.com/api/1.0"