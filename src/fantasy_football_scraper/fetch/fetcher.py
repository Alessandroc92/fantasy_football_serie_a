import asyncio

from fantasy_football_scraper import config
from niquests import AsyncResponse, AsyncSession


async def async_request(
    url: str,
    proxies: str | None = None,
    pool_maxsize: int = config.POOL_MAXSIZE,
) -> AsyncResponse:
    async with AsyncSession(pool_maxsize=pool_maxsize, timeout=config.TIMEOUT) as session:
        status_code = 500
        while status_code == 500:
            try:
                response = await session.get(url)
                status_code == 200
                return response
            except Exception as exe:
                await asyncio.sleep(2)


async def request_cycle(
    urls: lists[str], proxies: str | None = None
) -> list[AsyncResponse]:
    tasks = [async_request(url) for url in urls]
    responses = await asyncio.gather(*tasks)
    return responses
