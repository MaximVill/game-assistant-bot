import aiohttp
from config import CHEAPSHARK_BASE_URL

# Сервис для работы с CheapShark API
class CheapSharkService:
    # Инициализация сервиса с базовым URL
    def __init__(self):
        self.base_url = CHEAPSHARK_BASE_URL

    # Поиск внутреннего ID игры по названию
    async def find_game_id(self, game_name: str):
        params = {
            "title": game_name
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/games", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        # CheapShark API возвращает список объектов
                        if isinstance(data, list):
                            results = data
                        elif isinstance(data, dict) and "data" in data:
                            results = data["data"]
                        else:
                            results = []

                        if results and len(results) > 0:
                            first_result = results[0]
                            if isinstance(first_result, dict):
                                return first_result.get("gameID")
                        return None
                    return None
            except Exception as e:
                # Ошибку теперь обрабатывает хендлер через логгер
                raise e

    # Получение лучших предложений по ID игры
    async def get_best_deals(self, game_id: str):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/game/{game_id}/dealist") as response:
                    if response.status == 200:
                        return await response.json()
                    return None
            except Exception as e:
                raise e
