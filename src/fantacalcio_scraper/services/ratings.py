from fantacalcio_scraper.parse import html_parsing
from fantacalcio_scraper.fetch import fetcher, urls
from itertools import chain
import asyncio


async def extract_ratings(start_season: int, end_season: int):
    matchday_urls = urls.create_matchday_urls(
        start_season=start_season, end_season=end_season, max_games=1
    )
    matchday_responses = await fetcher.request_cycle(urls=matchday_urls)
    match_paths = [
        html_parsing.parse_match_urls(response.text) for response in matchday_responses
    ]
    match_urls = list(
        chain.from_iterable(
            urls.create_matches_urls(matchday_url, match_path)
            for matchday_url in matchday_urls
            for match_path in match_paths
        )
    )
    match_responses = await fetcher.request_cycle(urls=match_urls)
    match_info = [
        html_parsing.parse_match_info(match_response.text)
        for match_response in match_responses
    ]
    player_ratings = [
        html_parsing.parse_player_ratings(match_response.text)
        for match_response in match_responses
    ]
    print(player_ratings)


if __name__ == "__main__":
    test = asyncio.run(extract_ratings(2026, 2026))
    print(test)
