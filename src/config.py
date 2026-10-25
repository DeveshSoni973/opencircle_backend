import os
from dotenv import load_dotenv

load_dotenv()


class ServerConfig:
  host = os.getenv("SERVER_HOST", "127.0.0.1")
  port = int(os.getenv("SERVER_PORT", 8000))
  reload = os.getenv("RELOAD", "true").lower() in ("true", "1", "t")
  encryption_key = os.getenv("ENCRYPTION_KEY")
  # comma-separated origins allowed to call the API from a browser (the frontend dev server)
  cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")


class DatabaseConfig:
  url = os.getenv("DATABASE_URL", "sqlite:///./opencircle.db")
  echo = True


class Config:
  server = ServerConfig()
  database = DatabaseConfig()


config = Config()