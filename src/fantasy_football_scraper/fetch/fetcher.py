import asyncio
import itertools

from fantasy_football_scraper import config
from niquests import AsyncResponse, AsyncSession


async def async_request(
    session: AsyncSession,
    url: str,
) -> AsyncResponse:

    for _ in range(config.MAX_CLIENT_REQUESTS):
        try:
            return await session.get(url)
        except Exception:
            await asyncio.sleep(2)


async def request_cycle(
    urls: list[str],
    proxies: str | None = None,
) -> list[AsyncResponse]:

    async with AsyncSession(
        pool_maxsize=config.POOL_MAXSIZE,
        timeout=config.TIMEOUT,
        proxies=proxies,
    ) as session:

        tasks = [
            async_request(session, url)
            for url in urls
        ]

        return await asyncio.gather(*tasks)