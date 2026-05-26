import aiohttp
from bs4 import BeautifulSoup

# Сервис для скрапинга новостей с stopgame.ru
class StopGameService:
    URL = "https://stopgame.ru/news"

    # Сбор 5 последних новостей из индустрии
    async def get_latest_news(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.URL) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        news = []
                        # Поиск всех ссылок, которые ведут на страницы новостей
                        links = soup.find_all("a", href=True)
                        for link in links:
                            href = link["href"]
                            if "/newsdata/" in href:
                                title = link.text.strip()
                                if title:
                                    full_link = href if href.startswith("http") else f"https://stopgame.ru{href}"
                                    news.append({"title": title, "link": full_link})

                            if len(news) >= 5:
                                break

                        return news
                    return None
            except Exception as e:
                raise e
