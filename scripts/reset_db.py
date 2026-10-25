"""Hard reset: drop EVERY table in the database, then recreate the schema from the current models.

Use it whenever the DB and the code drift apart (removed/renamed columns, stale tables).
All data is deleted. Drops whatever tables exist in the DB, not just the ones the code knows about.

    uv run python scripts/reset_db.py --yes
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import MetaData  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402

import src.db  # noqa: E402,F401  -- registers every model on SQLModel.metadata
from src.db.db_connection import engine  # noqa: E402

if "--yes" not in sys.argv:
    sys.exit(f"This deletes ALL data in {engine.url}. Re-run with --yes to confirm.")

engine.echo = False

if engine.dialect.name == "sqlite" and engine.url.database:
    db_file = Path(engine.url.database)
    if db_file.exists():
        backup = db_file.with_name(f"{db_file.stem}.backup-{datetime.now():%Y%m%d-%H%M%S}{db_file.suffix}")
        shutil.copy2(db_file, backup)
        print(f"Backup: {backup}")

existing = MetaData()
existing.reflect(bind=engine)  # what is actually in the DB, regardless of the code
existing.drop_all(bind=engine)  # drops in foreign-key order
print(f"Dropped: {', '.join(sorted(existing.tables)) or '(no tables)'}")

SQLModel.metadata.create_all(engine)
print(f"Created: {', '.join(sorted(SQLModel.metadata.tables))}")
