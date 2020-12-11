import aiohttp
from lxml import html

from tracking import requests

_XPATH = '//html/body/div/main/div[3]/aside/div/div/div/div[2]/span[2]/text()'
_URL = 'https://revivalstory.net/home'


async def get_online_count(session: aiohttp.ClientSession):
    response = await requests.get(session, _URL)
    if response is None:
        return None

    text = html.fromstring(await response.text())
    online_count = text.xpath(_XPATH)[0]
    if not online_count.isdigit():
        return None

    return int(online_count)


if __name__ == '__main__':
    import asyncio


    async def _main():
        async with aiohttp.ClientSession() as session:
            print(await get_online_count(session))


    asyncio.run(_main())
