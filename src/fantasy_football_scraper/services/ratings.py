import asyncio
from itertools import chain

from niquests import AsyncResponse

from fantasy_football_scraper import config
from fantasy_football_scraper.db import save_data
from fantasy_football_scraper.fetch import browser_fetch, fetcher, urls
from fantasy_football_scraper.parse import html_parsing


async def extract_match_urls(
    start_season: int,
    end_season: int,
    matchday: int | None = None,
    n_matchdays: int = config.MAX_MATCHDAYS,
) -> list[str]:

    matchday_urls = urls.create_matchday_urls(
        start_season=start_season,
        end_season=end_season,
        n_matchdays=n_matchdays,
        matchday=matchday,
    )
    matchday_responses = await fetcher.request_cycle(urls=matchday_urls)
    match_urls = list(
        chain.from_iterable(
            html_parsing.parse_match_urls(response.text)
            for response in matchday_responses
        )
    )
    return match_urls


def extract_match_info(match_responses: list[str]) -> list[dict]:
    match_info = list(
        filter(
            None,
            [
                html_parsing.parse_match_info(match_response)
                for match_response in match_responses
            ],
        )
    )
    return match_info


def extract_teams(match_info: list[dict]) -> set[str]:
    teams = {mi["home_team"] for mi in match_info}.union(
        {mi["away_team"] for mi in match_info}
    )
    return teams


def extract_player_ratings(match_responses: list[str]) -> list[dict]:
    player_ratings = list(
        chain.from_iterable(
            html_parsing.parse_player_ratings(match_response)
            for match_response in match_responses
        )
    )
    return player_ratings


def extract_player_urls(player_ratings: list[dict]) -> list[str]:
    player_urls = list({pl["url"] for pl in player_ratings})
    return player_urls


def extract_player_data(player_responses: list[AsyncResponse]) -> list[dict]:
    player_data = [
        html_parsing.parse_player_data(player_response.text)
        for player_response in player_responses
    ]
    player_data = list(filter(None, player_data))
    return player_data


async def run_extraction_pipeline(
    driver_path: str,
    start_season: int,
    end_season: int,
    matchday: int | None = None,
    n_matchdays: int = config.MAX_MATCHDAYS,
) -> dict[str, int]:
    match_urls = await extract_match_urls(
        start_season=start_season,
        end_season=end_season,
        matchday=matchday,
        n_matchdays=n_matchdays,
    )
    match_responses = await browser_fetch.async_browsers(
        urls=match_urls, driver_path=driver_path
    )
    match_info = extract_match_info(match_responses)
    teams = extract_teams(match_info)
    player_ratings = extract_player_ratings(match_responses)
    player_urls = extract_player_urls(player_ratings)

    player_responses = await fetcher.request_cycle(urls=player_urls)
    player_data = extract_player_data(player_responses)

    save_data.save_teams(teams=teams)
    save_data.save_match_info(match_info=match_info)
    save_data.save_player_data(player_data=player_data)
    save_data.save_player_ratings(player_ratings=player_ratings)

    return {
        "teams": len(teams),
        "matches": len(match_info),
        "players": len(player_data),
        "ratings": len(player_ratings),
    }


if __name__ == "__main__":
    driver_path = browser_fetch.resolve_driver_path()
    start_season = 2016
    end_season = 2016
    matchday = None
    n_matchdays = 38
    recap = asyncio.run(
        run_extraction_pipeline(
            driver_path=driver_path,
            start_season=start_season,
            end_season=end_season,
            n_matchdays=n_matchdays,
            matchday=matchday,
        )
    )
