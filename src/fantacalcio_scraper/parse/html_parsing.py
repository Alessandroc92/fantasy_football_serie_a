from bs4 import BeautifulSoup
import datetime
from typing import Any


def extract_match_urls(html: str) -> list[str]:
    bs = BeautifulSoup(html, "html.parser")
    options = bs.select("select#matchControl option")
    return [option.get("value") for option in options if option.get("value")]


def extract_match_info(html: str) -> dict[Any]:
    bs = BeautifulSoup(html, "html.parser")
    match_date = bs.select_one(".match-date meta").attrs["content"]
    match_time = bs.select_one(".match-date .hours").get_text()
    home_team = bs.select_one(".team-home a.team-name meta").attrs["content"]
    away_team = bs.select_one(".team-away a.team-name meta").attrs["content"]
    home_score = bs.select_one(".score-home").get_text()
    away_score = bs.select_one(".score-away").get_text()
    return {
        "home_team": home_team,
        "home_score": home_score,
        "away_score": away_score,
        "away_team": away_team,
        "match_date": datetime.datetime.strptime(
            f"{match_date} {match_time}", "%Y-%m-%d %H:%M"
        ),
    }

def extract_player_ratings(
    html: str
) -> list[dict[Any]]:
    bs = BeautifulSoup(html, 'html.parser')
    player_infos = bs.find_all(class_='player-info')
    player_ratings = []
    for player in player_infos:
        player_ratings.append({
            "player_name": player.select('.player-name span')[0].get_text()
        })
    return player_ratings
    

if __name__ == "__main__":
    with open(
        "/Users/ale/Desktop/altro.html"
    ) as file:
        html = file.read()
    print(extract_player_ratings(html=html))
