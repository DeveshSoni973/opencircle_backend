from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from src.config import config
from src.common.error import AppError
from src.common.error_handler import app_error_handler
from src.db.db_connection import create_db_and_tables
from src.db import providers  # noqa: F401  -- so create_all sees the table
from src.modules.provider import router as provider_router


@asynccontextmanager
async def lifespan(app: FastAPI):
  create_db_and_tables()
  yield


app = FastAPI(lifespan=lifespan)
app.add_exception_handler(AppError, app_error_handler)
app.include_router(provider_router)

@app.get("/")
def read_root():
  return {"Hello": "World"}


def main():
  
  uvicorn.run(
      "src.main:app",
      host=config.server.host,
      port=config.server.port,
      reload=config.server.reload,
  )


if __name__ == "__main__":
  main()