import asyncio
import xml.etree.ElementTree as ET
import aiohttp


class StopGameService:
    # Основной источник (StopGame RSS)
    PRIMARY_URL = "https://stopgame.ru/rss/news.xml"

    # Резервный источник (PlayGround RSS — очень стабильный, без защиты от ботов)
    FALLBACK_URL = "https://www.playground.ru/rss/news.xml"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/xml, text/xml, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://stopgame.ru/"
    }

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def get_latest_news(self):
        # 1. Пробуем получить новости из основного источника
        news = await self._fetch_rss(self.PRIMARY_URL)
        if news:
            return news

        # 2. Если основной источник недоступен/заблокирован, пробуем резервный
        print("[Warning] Основной источник новостей заблокирован или недоступен. Пробую резервный...")
        news = await self._fetch_rss(self.FALLBACK_URL)
        return news

    async def _fetch_rss(self, url: str):
        try:
            # Ограничиваем время ожидания до 8 секунд
            timeout = aiohttp.ClientTimeout(total=8)
            async with self.session.get(url, headers=self.HEADERS, timeout=timeout) as response:
                if response.status == 200:
                    # Читаем байты (response.read()) вместо текста.
                    # Это предотвращает краш парсера при несовпадении кодировок XML.
                    raw_data = await response.read()

                    root = await asyncio.to_thread(ET.fromstring, raw_data)

                    news_list = []
                    for item in root.findall('.//item'):
                        title_elem = item.find('title')
                        link_elem = item.find('link')

                        if title_elem is not None and link_elem is not None:
                            title = " ".join(title_elem.text.split()) if title_elem.text else ""
                            link = link_elem.text.strip() if link_elem.text else ""

                            if title and link:
                                news_list.append({
                                    "title": title,
                                    "link": link
                                })

                        if len(news_list) >= 5:
                            break

                    return news_list
                else:
                    print(f"[News Service] Источник {url} вернул статус-код: {response.status}")
                    return None
        except Exception as e:
            print(f"[News Service] Ошибка при запросе к {url}: {e}")
            return None