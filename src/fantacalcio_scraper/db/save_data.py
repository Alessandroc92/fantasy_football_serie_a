from psycopg2.errors import UniqueViolation
from sqlalchemy import Engine, func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from fantacalcio_scraper.db import db_engine
from fantacalcio_scraper.db.models import Match, Player, Rating, Team, PlayerStats


def save_data(session: Session, object_instance: object):
    try:
        session.add(object_instance)
        session.commit()
    except IntegrityError, UniqueViolation:
        session.rollback()


def save_teams(teams: set, engine: Engine = db_engine.engine) -> None:
    with Session(bind=engine) as session:
        for team in teams:
            save_data(session=session, object_instance=Team(team_name=team))


def save_match_info(match_info: list[dict], engine: Engine = db_engine.engine) -> None:
    with Session(bind=engine) as session:
        for match_data in match_info:
            ht_query = select(Team.id).where(
                Team.team_name == match_data.pop("home_team")
            )
            match_data["home_team_id"] = session.exec(ht_query).first()
            at_query = select(Team.id).where(
                Team.team_name == match_data.pop("away_team")
            )
            match_data["away_team_id"] = session.exec(at_query).first()
            save_data(session=session, object_instance=Match.model_validate(match_data))


def save_player_data(
    player_data: list[dict], engine: Engine = db_engine.engine
) -> None:
    with Session(bind=engine) as session:
        for player in player_data:
            save_data(session=session, object_instance=Player.model_validate(player))
            team_query = select(Team.id).filter(
                func.lower(Team.team_name) == func.lower(player["team"])
            )
            player["team_id"] = session.exec(team_query).first()
            save_data(session=session, object_instance=PlayerStats.model_validate(player))


def save_player_ratings(
    player_ratings: list[dict], engine: Engine = db_engine.engine
) -> None:
    with Session(bind=engine) as session:
        for rating in player_ratings:
            team_query = select(Team.id).filter(
                func.lower(Team.team_name) == func.lower(rating["team"])
            )
            rating["team_id"] = session.exec(team_query).first()
            save_data(session=session, object_instance=Rating.model_validate(rating))
