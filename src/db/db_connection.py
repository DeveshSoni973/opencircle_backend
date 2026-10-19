from sqlalchemy import event
from sqlmodel import create_engine, Session, SQLModel
from src.config import config

engine = create_engine(
    config.database.url,
    connect_args={"check_same_thread": False},
    echo=config.database.echo,
)


@event.listens_for(engine, "connect")
def _enable_sqlite_fk(dbapi_conn, _record):
    # SQLite ignores foreign keys unless this is set on every connection
    if engine.dialect.name == "sqlite":
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session