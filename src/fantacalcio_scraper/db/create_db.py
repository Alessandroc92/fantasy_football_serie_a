
from sqlalchemy import URL, Engine
from sqlmodel import create_engine, SQLModel
from fantacalcio_scraper.db import db_engine


def create_tables(engine: Engine):
    SQLModel.metadata.create_all(bind=engine)


if __name__ == '__main__':
    from fantacalcio_scraper.db import models
    create_tables(engine=db_engine.engine)