from sqlmodel import Session, select
from fantacalcio_scraper.db import db_engine
from fantacalcio_scraper.db.models import Team, Match, Rating, Player, PlayerStats
from sqlalchemy import Engine, func
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation


def save_teams(teams: set, engine: Engine=db_engine.engine) -> None:
    team_objects = [Team(team_name=team) for team in teams]
    with Session(bind=engine) as session:
        try:
            session.add_all(team_objects)
            session.commit()
        except Exception as UniqueViolation:
            session.rollback()
            
            
def save_match_info(match_info: list[dict], engine: Engine=db_engine.engine) -> None:
    with Session(bind=engine) as session:
        for match_data in match_info:
            ht_query = select(Team.id).where(Team.team_name == match_data.pop("home_team"))
            match_data["home_team_id"] = session.exec(ht_query).first()
            at_query = select(Team.id).where(Team.team_name == match_data.pop("away_team"))
            match_data["away_team_id"] = session.exec(at_query).first()
            try:
                session.add(Match(**match_data))
                session.commit()
            except IntegrityError:
                session.rollback()
                
def save_player_data(player_data: list[dict], engine: Engine=db_engine.engine) -> None:
    with Session(bind=engine) as session:
        for player in player_data:
            player_object = Player(**player)
            try:
                session.add(player_object)
            except:
                pass
                
                

def save_player_ratings(player_ratings: list[dict], engine: Engine=db_engine.engine)-> None:
    with Session(bind=engine) as session:
        for rating in player_ratings:
            print(rating["player_team"])
            team_query = select(Team.id).filter(func.lower(Team.team_name) == func.lower(rating["player_team"]))
            rating['team_id'] = session.exec(team_query).first()
            print(rating)
            try:
                session.add(Rating(**rating))
                session.commit()
            except:
                print('sto qua')
                session.rollback()
                
                

