import aiohttp
from config import CHEAPSHARK_BASE_URL

class CheapSharkService:
    def __init__(self, session: aiohttp.ClientSession):
        self.base_url = CHEAPSHARK_BASE_URL
        self.session = session
        self.stores_cache = {}

    async def pre_fetch_stores(self):
        """Скачивает и кэширует список магазинов при запуске бота."""
        try:
            stores = await self.get_stores()
            if stores:
                self.stores_cache = {s['storeID']: s['storeName'] for s in stores}
        except Exception as e:
            print(f"[Warning] Не удалось кэшировать магазины CheapShark: {e}")

    async def find_game_id(self, game_name: str):
        params = {"title": game_name}
        try:
            async with self.session.get(f"{self.base_url}/games", params=params) as response:
                if response.status == 200:
                    data = await response.json()
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
            raise e

    async def get_best_deals(self, game_id: str):
        params = {"id": game_id}
        try:
            async with self.session.get(f"{self.base_url}/games", params=params) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            raise e

    async def get_stores(self):
        try:
            async with self.session.get(f"{self.base_url}/stores") as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            raise e