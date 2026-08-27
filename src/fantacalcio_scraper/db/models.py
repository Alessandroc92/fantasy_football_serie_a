import datetime
import re

from dateutil import parser
from pydantic import field_validator
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, SQLModel

from fantacalcio_scraper import config


class Team(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    team_name: str = Field(unique=True)


class Match(SQLModel, table=True):
    fc_match_id: int = Field(primary_key=True)
    home_team_id: int = Field(foreign_key="team.id")
    away_team_id: int = Field(foreign_key="team.id")
    home_score: int
    away_score: int
    match_date: datetime.datetime


class Rating(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    fc_match_id: int = Field(foreign_key="match.fc_match_id")
    fc_player_id: int = Field(foreign_key="player.fc_player_id")
    team_id: int = Field(foreign_key="team.id")
    rating: float
    bonus_malus: list[dict] | list[None] = Field(sa_column=Column(JSONB))

    @field_validator("rating", mode="before")
    @classmethod
    def validate_rating(cls, value: str) -> float:
        return float(value.replace(",", "."))


class Player(SQLModel, table=True):
    fc_player_id: int = Field(primary_key=True)
    name: str
    slug: str
    birthdate: datetime.date
    height: int
    foot: str
    nationality: list[str] = Field(sa_column=Column(JSONB))

    @field_validator("birthdate", mode="before")
    @classmethod
    def validate_birthdate(cls, value: str):
        ita_month = re.search(r"[a-z]{3,4}", value).group(0)
        en_month = config.ITALIAN_MONTHS_MAPPING.get(ita_month)
        birthdate = value.replace(ita_month, en_month)
        return parser.parse(birthdate).date()

    @field_validator("height", mode="before")
    @classmethod
    def validate_height(cls, value: str):
        return value.replace("cm", "")

    @field_validator("nationality", mode="before")
    @classmethod
    def validate_nationality(cls, value: str):
        return value.split(",")


class PlayerStats(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    fc_player_id: int = Field(foreign_key="player.fc_player_id")
    team_id: int = Field(foreign_key="team.id")
    main_role: str
    specific_roles: list = Field(sa_column=Column(JSONB))
    classic_value: int
    classic_vfm: int
    mantra_value: int
    mantra_vfm: int
    season: int
    date: datetime.datetime = Field(default_factory=datetime.datetime.now)
