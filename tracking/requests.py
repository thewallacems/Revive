import asyncio
from typing import Optional

import aiohttp


async def get(session: aiohttp.ClientSession, url: str, params: Optional[dict] = None, *, retries=5):
    response = await session.get(url, params=params)

    if response.status == 200:
        return response
    else:
        if retries > 0:
            await asyncio.sleep(1.0)
            return await get(session, url, params, retries=retries - 1)
        else:
            return None
