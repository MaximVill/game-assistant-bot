import aiohttp
from config import RAWG_API_KEY, RAWG_BASE_URL

class RAWGService:
    def __init__(self, session: aiohttp.ClientSession):
        self.api_key = RAWG_API_KEY
        self.base_url = RAWG_BASE_URL
        self.session = session

    async def search_game(self, query: str):
        params = {
            "key": self.api_key,
            "search": query,
            "page_size": 5
        }
        try:
            async with self.session.get(f"{self.base_url}/games", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                return None
        except Exception as e:
            print(f"RAWG Search Error: {e}")
            raise e

    async def get_game_details(self, game_id: int):
        params = {"key": self.api_key}
        try:
            async with self.session.get(f"{self.base_url}/games/{game_id}", params=params) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            print(f"RAWG Details Error: {e}")
            raise e