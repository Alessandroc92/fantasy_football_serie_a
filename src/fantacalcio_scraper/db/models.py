from sqlmodel import SQLModel, Field, PrimaryKeyConstraint, ForeignKey
from pydantic import UrlConstraints


class Team(SQLModel, table=True):
    team_name: str = Field(alias=['home_team','away_team'])
    
    
class Match(SQLModel, table=True):
    fc_match_id: int
    home_team: Team
    away_team: Team
    home_score: int 
    away_score: int
    match_date: datetime
    
    
class Rating(SQLModel, table=True):
    fc_match: Match
    fc_player_id: int
    player_slug: str
    player_team: Team 
    player_rating: int
    player_url: UrlConstraints
    player_bonus_malus: list[dict]
    

class BonusMalus(SQLModel, table=True):
    rating: ForeignKey
    

    