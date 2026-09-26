from sqlmodel import create_engine, Session, SQLModel
from pathlib import Path
from src.config import config

engine = create_engine(
    config.database.url,
    connect_args={"check_same_thread": False},
    echo=config.database.echo,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session