import datetime
import re
from typing import Any

from bs4 import BeautifulSoup


def parse_match_urls(html: str) -> list[str]:
    bs = BeautifulSoup(html, "html.parser")
    options = bs.select("select#matchControl option")
    values = [option.get("value") for option in options if option.get("value")]
    paths = [
        f"{m.group(1)}-{m.group(2)}/{m.group(3)}"
        for m in (re.search(r"/?([a-zA-Z]+)/([a-zA-Z]+)/(\d{1,10})", v) for v in values)
        if m
    ]
    return paths


def parse_match_info(html: str) -> dict[Any]:
    bs = BeautifulSoup(html, "html.parser")
    match_date = bs.select_one(".match-date meta").attrs["content"]
    match_time = bs.select_one(".match-date .hours").get_text()
    match_url = bs.select_one("select#matchControl option[selected]").get("value")
    return {
        "fc_match_id": re.search(r'/([0-9]+)', match_url).group(1),
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
    match_url = bs.select_one("select#matchControl option[selected]").get("value")
    player_ratings = []
    for player in player_infos:
        player_url = player.select_one(".player-name").attrs.get("href")
        bonus_malus = player.select(".icon.bonus-icon")
        player_ratings.append(
            {   "player_url": player_url,
                "fc_match_id": re.search(r'/([0-9]+)', match_url).group(1),
                "fc_player_id": re.search(r"/(\d{1,8})/", player_url).group(1),
                "player_slug": re.search(r"/([^/]+)/[0-9]+", player_url).group(1),
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
    try:
        return {
            "name": bs.select_one(".h5.player-name").get_text(),
            "team": bs.select_one(".team-name.team-link meta").get("content"),
            "height": bs.select_one("dd[itemprop='height']").get_text(),
            "birthdate": bs.select_one(".birthdate").get_text(),
            "foot": bs.select_one("span[title='Sinistro'], span[title='Destro']").get_text(),
            "nationality": bs.select_one(".nationalities").get_text(),
            "main_role": bs.select_one(".role").get('title'),
            "specific_roles": [role.get('title') for role in bs.select('.role.role-mantra')],
            "classic_value": bs.select_one("li[title='Quotazione classic'] .badge.badge-primary").get_text(),
            "mantra_value": bs.select_one("li[title='Quotazione Mantra'] .badge.badge-alternative").get_text(),
            "classic_vfm": bs.select_one("li[title='FantaValore di Mercato (Classic)'] .badge.badge-primary").get_text(),
            "mantra_vfm": bs.select_one("li[title='FantaValore di Mercato (Mantra)'] .badge.badge-alternative").get_text(),
        }
    except:
        return None


if __name__ == "__main__":
    with open(
        "/Users/ale/Desktop/coding/projects/personal/fantacalcio/data/ratings_3.html"
    ) as file:
        html = file.read()
    print(parse_player_ratings(html=html))
