import aiohttp
from config import RAWG_API_KEY, RAWG_BASE_URL

# Сервис для работы с RAWG API
class RAWGService:
    # Инициализация сервиса с API ключом и базовым URL
    def __init__(self):
        self.api_key = RAWG_API_KEY
        self.base_url = RAWG_BASE_URL

    # Поиск игр через RAWG API
    async def search_game(self, query: str):
        params = {
            "key": self.api_key,
            "search": query,
            "page_size": 5
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/games", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [])
                    return None
            except Exception as e:
                print(f"RAWG Search Error: {e}")
                return None

    # Получение детальной информации о конкретной игре
    async def get_game_details(self, game_id: int):
        params = {
            "key": self.api_key
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/games/{game_id}", params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
            except Exception as e:
                print(f"RAWG Details Error: {e}")
                return None
