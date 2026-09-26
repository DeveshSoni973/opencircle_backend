import os
from dotenv import load_dotenv

load_dotenv()


class ServerConfig:
  host = os.getenv("SERVER_HOST", "127.0.0.1")
  port = int(os.getenv("SERVER_PORT", 8001))
  reload = os.getenv("RELOAD", "true").lower() in ("true", "1", "t")


class DatabaseConfig:
  url = os.getenv("DATABASE_URL", "sqlite:///./opencircle.db")
  echo = True


class Config:
  server = ServerConfig()
  database = DatabaseConfig()


config = Config()