from fantasy_football_scraper.db import db_engine
from sqlalchemy import Engine
from sqlmodel import SQLModel


def create_tables(engine: Engine):
    SQLModel.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables(engine=db_engine.engine)
