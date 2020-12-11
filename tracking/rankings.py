from datetime import datetime

import aiohttp
from lxml import html

from tracking import requests

_FMT_TIME = '%m/%d/%Y %H:%M:%S'

_PAGES_XPATH = '//*[@id="page-content-container"]/div/div/div/div[3]/center/ul/li'
_CHARACTERS_XPATH = '//*[@id="page-content-container"]/div/div/div/div[3]/table/tbody/tr'

_URL = 'https://revivalstory.net/rankings?filter=overall&page=1'
_PAGE_URL = 'https://revivalstory.net/rankings?filter=overall&page={0}'


async def get_rankings(session: aiohttp.ClientSession):
    last_page = await _get_last_ranking_page(session)
    if last_page is None:
        return None

    time = datetime.utcnow().strftime(_FMT_TIME).split(' ')
    date = time[0]
    time = time[1]

    characters = []

    for index in range(last_page):
        url = _PAGE_URL.format(index + 1)
        response = await requests.get(session, url)
        if response is None:
            return None

        text = html.fromstring(await response.text())
        rankings = text.xpath(_CHARACTERS_XPATH)[2:]

        for character in rankings:
            level = int(character[-1].text_content().strip())
            if level < 2:
                continue

            name = character[-3].text_content().strip()
            job = character[-2].text_content().strip()

            characters.append((date, time, name, job, level))

    return characters


async def _get_last_ranking_page(session: aiohttp.ClientSession):
    response = await requests.get(session, _URL)
    if response is None:
        return None

    tree = html.fromstring(await response.text())
    xpath = tree.xpath(_PAGES_XPATH)
    if not xpath:
        return None

    try:
        return int(xpath[-2].text_content())
    except:
        return 1


if __name__ == '__main__':
    import asyncio


    async def _main():
        async with aiohttp.ClientSession() as session:
            print(await get_rankings(session))


    asyncio.run(_main())
