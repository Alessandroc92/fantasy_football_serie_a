import datetime
import re
from typing import Any

from bs4 import BeautifulSoup


def parse_match_urls(html: str) -> list[str]:
    bs = BeautifulSoup(html, "html.parser")
    options = bs.select("select#matchControl option")
    return [option.get("value") for option in options if option.get("value")]


def parse_match_info(html: str) -> dict[Any]:
    bs = BeautifulSoup(html, "html.parser")
    match_date = bs.select_one(".match-date meta").attrs["content"]
    match_time = bs.select_one(".match-date .hours").get_text()
    return {
        "home_team": bs.select_one(".team-home a.team-name meta").get("content"),
        "home_score": bs.select_one(".score-home").get_text(),
        "away_score": bs.select_one(".score-away").get_text(),
        "away_team": bs.select_one(".team-away a.team-name meta").get("content"),
        "match_date": datetime.datetime.strptime(
            f"{match_date} {match_time}", "%Y-%m-%d %H:%M"
        ),
    }


def parse_player_ratings(html: str) -> list[dict[Any]]:
    bs = BeautifulSoup(html, "html.parser")
    player_infos = bs.find_all(class_="player-info")
    player_ratings = []
    for player in player_infos:
        player_url = player.select_one(".player-name").attrs.get("href")
        bonus_malus = player.select(".icon.bonus-icon")
        player_ratings.append(
            {
                "player_id": re.search(r"/(\d{1,8})/", player_url).group(1),
                "player_slug": re.search(r"/([a-z-]+)+/[0-9]+", player_url).group(1),
                "player_team": re.search(r"/squadre/([a-z]+)/", player_url).group(1),
                "player_rating": player.select_one(".badge.grade").get_text(),
                "player_bonus_malus": []
                if not bonus_malus
                else [{bm.get("title"): bm.get("data-value")} for bm in bonus_malus],
            }
        )
    return player_ratings


def parse_player_data(html: str) -> dict:
    bs = BeautifulSoup(html, "html.parser")
    return {
        "player_name": bs.select_one(".h5.player-name").get_text(),
        "player_team": bs.select_one(".team-name.team-link meta").get("content"),
        "player_height": bs.select_one("dd[itemprop='height']").get_text(),
        "player_birthdate": bs.select_one(".birthdate").get_text(),
        "player_foot": bs.select_one("span[title='Sinistro'], span[title='Destro']").get_text(),
        "player_nationality": bs.select_one(".nationalities").get_text(),
        "player_main_role": bs.select_one(".role").get('title'),
        "player_specific_roles": [role.get('title') for role in bs.select('.role.role-mantra')],
        "player_value_classic": bs.select_one("li[title='Quotazione classic'] .badge.badge-primary").get_text(),
        "player_value_mantra": bs.select_one("li[title='Quotazione Mantra'] .badge.badge-alternative").get_text(),
        "player_vfm_classic": bs.select_one("li[title='FantaValore di Mercato (Classic)'] .badge.badge-primary").get_text(),
        "player_vfm_mantra": bs.select_one("li[title='FantaValore di Mercato (Mantra)'] .badge.badge-alternative").get_text(),
    }


if __name__ == "__main__":
    with open(
        "/Users/ale/Desktop/coding/projects/personal/fantacalcio/data/player_2.html"
    ) as file:
        html = file.read()
    print(parse_player_data(html=html))
