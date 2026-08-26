import datetime
import re

from dateutil import parser
from pydantic import AliasChoices, UrlConstraints, field_validator
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, ForeignKey, PrimaryKeyConstraint, SQLModel

from fantacalcio_scraper import config


class Team(SQLModel, table=True):
    id: int = Field(alias='id', primary_key=True)
    team_name: str = Field(unique=True)
    
    
class Match(SQLModel, table=True):
    fc_match_id: int = Field(primary_key=True)
    home_team_id: int = Field(foreign_key='team.id')
    away_team_id: int = Field(foreign_key='team.id')
    home_score: int 
    away_score: int
    match_date: datetime.datetime
    
    
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
    birthdate: datetime.date
    height: int 
    foot: str 
    nationality: str
    
    
    @field_validator('birthdate', mode='before')
    @classmethod
    def validate_birthdate(cls, value: str):
        ita_month = re.search(r'[a-z]{3,4}',value).group(0)
        en_month = config.ITALIAN_MONTHS_MAPPING[ita_month]
        birthdate = value.replace(ita_month, en_month)
        return parser.parse(birthdate).date()
    
    @field_validator('height', mode='before')
    @classmethod
    def validate_height(cls, value: str):
        return value.replace('cm','')
    

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
    date: datetime.datetime = Field(default_factory=datetime.datetime.now)


if __name__ == '__main__':
    p = { 'birthdate': '26 mag 2001',
    'classic_value': '15',
    'classic_vfm': '23',
    'foot': 'Sx',
    'height': '170cm',
    'main_role': 'Centrocampista',
    'mantra_value': '15',
    'mantra_vfm': '23',
    'name': 'Adrian Bernabè',
    'nationality': 'Spagna',
    'specific_roles': ['Centrocampista centrale'],
    'team': 'Parma'}
    pl = Player.validate(p)
    print(pl)