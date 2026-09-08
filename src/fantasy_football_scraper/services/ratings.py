import asyncio
import pprint
from itertools import chain

from fantasy_football_scraper.db import save_data
from fantasy_football_scraper.fetch import fetcher, urls
from fantasy_football_scraper.parse import html_parsing



async def extract_ratings(start_season: int, end_season: int):
    matchday_urls = urls.create_matchday_urls(
        start_season=start_season, end_season=end_season, n_matchdays=2
    )
    
    matchday_responses = await fetcher.request_cycle(urls=matchday_urls)
    match_urls = list(
        chain.from_iterable(
            html_parsing.parse_match_urls(response.text)
            for response in matchday_responses
            if response.status_code == 200
        )
    )
    match_responses = await fetcher.request_cycle(urls=match_urls)

    match_info = list(
        filter(
            lambda x: x if x else None,
            [
                html_parsing.parse_match_info(match_response.text)
                for match_response in match_responses
            ],
        )
    )
    teams = {mi["home_team"] for mi in match_info}.union(
        {mi["away_team"] for mi in match_info}
    )
    save_data.save_teams(teams=teams)
    save_data.save_match_info(match_info=match_info)

    player_ratings = list(
        chain.from_iterable(
            [
                html_parsing.parse_player_ratings(match_response.text)
                for match_response in match_responses
            ]
        )
    )
    player_urls = list({pl["url"] for pl in player_ratings})
    player_responses = await fetcher.request_cycle(urls=player_urls)
    player_data = [
        html_parsing.parse_player_data(player_response.text)
        for player_response in player_responses
    ]
    # pprint.pprint(player_data, indent=2)
    save_data.save_player_data(
        player_data=list(filter(lambda x: x if x else None, player_data))
    )
    save_data.save_player_ratings(player_ratings=player_ratings)
    # pprint.pprint(player_ratings, indent=2)


if __name__ == "__main__":
    start_season = 2027
    end_season = 2027
    test = asyncio.run(extract_ratings(start_season=start_season, end_season=end_season))
    print(test)
