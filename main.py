import asyncio

from fantasy_football_scraper.fetch import browser_fetch
from fantasy_football_scraper.services import ratings


def main(
    start_season: int,
    end_season: int,
    n_matchdays: int,
    matchday: int,
):
    driver_path = browser_fetch.resolve_driver_path()
    asyncio.run(
        ratings.run_extraction_pipeline(
            driver_path=driver_path,
            start_season=start_season,
            end_season=end_season,
            matchday=matchday,
            n_matchdays=n_matchdays,
        )
    )


if __name__ == "__main__":
    start_season = end_season = 2027
    n_matchdays = 38
    matchday = 5
    main(
        start_season=start_season,
        end_season=end_season,
        n_matchdays=n_matchdays,
        matchday=matchday,
    )
