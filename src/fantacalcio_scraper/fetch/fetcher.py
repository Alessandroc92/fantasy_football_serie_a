from niquests import AsyncSession, AsyncResponse
import asyncio


async def async_request(url: str, proxies: str | None = None) -> AsyncResponse:
    async with AsyncSession() as session:
        return await session.get(url)
    
    
async def request_cycle(urls: lists[str], proxies: str | None = None) -> list[AsyncResponse]:
    tasks = [async_request(url) for url in urls]
    responses = await asyncio.gather(*tasks)
    return responses
