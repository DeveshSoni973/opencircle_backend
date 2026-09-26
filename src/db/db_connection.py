from sqlmodel import create_engine, Session, SQLModel
from pathlib import Path
from config.database import DATABASE_URL, ECHO_SQL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=ECHO_SQL,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session