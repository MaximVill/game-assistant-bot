import asyncio
import aiohttp
from bs4 import BeautifulSoup


class FreeSteamService:
    URL = "https://freesteam.ru/"

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def get_giveaways(self):
        try:
            async with self.session.get(self.URL) as response:
                if response.status == 200:
                    html_content = await response.text()

                    # Переносим парсинг в отдельный поток, чтобы не блокировать бота
                    soup = await asyncio.to_thread(BeautifulSoup, html_content, "html.parser")

                    giveaways = []
                    seen_links = set()
                    links = soup.find_all("a", href=True)

                    for link in links:
                        href = link["href"]
                        if "/razdacha-" in href:
                            base_href = href.split('#')[0]
                            title = link.text.strip()

                            if (
                                    title
                                    and not title.isdigit()
                                    and len(title) > 10
                                    and title.lower() not in ["читать далее", "комментарии", "подробнее"]
                            ):
                                full_link = base_href if base_href.startswith(
                                    "http") else f"https://freesteam.ru{base_href}"

                                if full_link not in seen_links:
                                    giveaways.append({"title": title, "link": full_link})
                                    seen_links.add(full_link)

                    return giveaways[:10]
                return None
        except Exception as e:
            raise e