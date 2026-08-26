from sqlmodel import SQLModel, Field, PrimaryKeyConstraint, ForeignKey, Column
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import UrlConstraints, AliasChoices
from datetime import datetime


class Team(SQLModel, table=True):
    id: int = Field(alias='id', primary_key=True)
    team_name: str = Field(unique=True)
    
    
class Match(SQLModel, table=True):
    fc_match_id: int = Field(primary_key=True)
    home_team_id: int = Field(foreign_key='team.id')
    away_team_id: int = Field(foreign_key='team.id')
    home_score: int 
    away_score: int
    match_date: datetime
    
    
class Rating(SQLModel, table=True):
    id: int = Field(alias='id', primary_key=True)
    fc_match_id: int = Field(foreign_key='match.fc_match_id')
    fc_player_id: int = Field(foreign_key='player.fc_player_id')
    team_id: int = Field(foreign_key='team.id')
    player_rating: int
    bonus_malus: dict = Field(sa_column=Column(JSONB))
    

class Player(SQLModel, table=True):
    fc_player_id: int = Field(primary_key=True)
    name: str
    birthdate: datetime
    height: int 
    foot: str 
    nationality: str
    

class PlayerStats(SQLModel, table=True):
    id: int = Field(primary_key=True)
    fc_player_id: int = Field(foreign_key='player.fc_player_id')
    team_id: int = Field(foreign_key='team.id')
    main_role: str
    specific_roles: dict = Field(sa_column=Column(JSONB))
    classic_value: int
    classic_vfm: int
    mantra_value: int
    mantra_vfm: int
    season: int
    date: datetime = Field(default_factory=datetime.now)
    