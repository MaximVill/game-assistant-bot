import asyncio
import aiohttp
from bs4 import BeautifulSoup


class StopGameService:
    URL = "https://stopgame.ru/news"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://stopgame.ru/"
    }

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def get_latest_news(self):
        try:
            async with self.session.get(self.URL, headers=self.HEADERS) as response:
                if response.status == 200:
                    html_content = await response.text()

                    # Переносим парсинг в отдельный поток, чтобы не блокировать бота
                    soup = await asyncio.to_thread(BeautifulSoup, html_content, "html.parser")

                    news = []
                    seen_links = set()
                    links = soup.find_all("a", href=True)

                    for link in links:
                        href = link["href"]
                        if "/show/" in href:
                            title = " ".join(link.text.split())

                            if title and len(title) > 12:
                                full_link = href if href.startswith("http") else f"https://stopgame.ru{href}"
                                if full_link not in seen_links:
                                    news.append({"title": title, "link": full_link})
                                    seen_links.add(full_link)

                            if len(news) >= 5:
                                break

                        return news
                    else:
                        print(f"[StopGame Error] Server returned status code: {response.status}")
                        return None
        except Exception as e:
            print(f"[StopGame Error] Exception occurred: {e}")
            raise e