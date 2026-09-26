from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parents[2]

# Database
DATABASE_URL = f"sqlite:///{BASE_DIR / 'opencircle.db'}"
ECHO_SQL = False                    # set True when debugging

# Optional future settings
# POOL_SIZE = 5
# MAX_OVERFLOW = 10