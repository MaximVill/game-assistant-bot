import aiohttp
from bs4 import BeautifulSoup

# Сервис для скрапинга раздач с freesteam.ru
class FreeSteamService:
    URL = "https://freesteam.ru/"

    # Сбор актуальных бесплатных раздач игр
    async def get_giveaways(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.URL) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        giveaways = []
                        # Используем более точные селекторы на основе анализа HTML
                        links = soup.find_all("a", href=True)
                        for link in links:
                            href = link["href"]
                            if "/razdacha-" in href:
                                title = link.text.strip()
                                if title:
                                    full_link = href if href.startswith("http") else f"https://freesteam.ru{href}"
                                    giveaways.append({"title": title, "link": full_link})

                        # Удаляем дубликаты, сохраняя порядок
                        seen = set()
                        unique_giveaways = []
                        for g in giveaways:
                            if g['link'] not in seen:
                                unique_giveaways.append(g)
                                seen.add(g['link'])

                        return unique_giveaways[:10]
                    return None
            except Exception as e:
                raise e
