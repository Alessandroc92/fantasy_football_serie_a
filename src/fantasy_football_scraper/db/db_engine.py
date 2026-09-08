from dotenv import load_dotenv
from sqlalchemy import URL, Engine
from sqlmodel import SQLModel, create_engine

load_dotenv()
import os

engine = create_engine(
    url=URL.create(
        drivername="postgresql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
    ),
)