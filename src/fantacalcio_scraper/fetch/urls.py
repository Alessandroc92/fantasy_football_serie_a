from urllib.parse import urljoin
import os
import dotenv
from fantacalcio_scraper import config

dotenv.load_dotenv()
BASE_URL = os.getenv("BASE_URL")


def create_matchday_url(season: int, matchday: int) -> str:
    matchday_url = f"calendario/{matchday}/{season - 1}-{season}"
    return urljoin(BASE_URL, matchday_url)


def create_matchday_urls(
    start_season: int, end_season: int, max_games: int = config.MAX_GAMES
) -> list[str]:
    urls = []
    for season in range(start_season, end_season + 1):
        urls_generation = [
            urls.append(create_matchday_url(season=season, matchday=matchday))
            for matchday in range(1, max_games + 1)
        ]
    return urls


def create_matches_urls(matchday_url: str, match_urls: list[str]):
    return [f'{matchday_url}/{match_url}/pagelle' for match_url in match_urls]