import asyncio

from fantasy_football_scraper import config
from niquests import AsyncResponse, AsyncSession


async def async_request(
    url: str,
    proxies: str | None = None,
    pool_maxsize: int = config.POOL_MAXSIZE,
) -> AsyncResponse:
    async with AsyncSession(pool_maxsize=pool_maxsize) as session:
        return await session.get(url)


async def request_cycle(
    urls: lists[str], proxies: str | None = None
) -> list[AsyncResponse]:
    tasks = [async_request(url) for url in urls]
    responses = await asyncio.gather(*tasks)
    return responses
