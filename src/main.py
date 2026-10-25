from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import config
from sqlalchemy.exc import IntegrityError
from src.common.error import AppError
from src.common.error_handler import app_error_handler, integrity_error_handler
from src.db.db_connection import create_db_and_tables
from src.db import providers, agents, groups, group_members, messages  # noqa: F401  -- so create_all sees every table
from src.modules.provider import router as provider_router
from src.modules.agent import router as agent_router
from src.modules.group import router as group_router
from src.modules.chat import router as chat_router
from src.modules.realtime import router as realtime_router
from src.modules.chat.manager import chat_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
  create_db_and_tables()
  yield
  await chat_manager.shutdown()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
  CORSMiddleware,
  allow_origins=config.server.cors_origins,
  allow_methods=["*"],
  allow_headers=["*"],
)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.include_router(provider_router)
app.include_router(agent_router)
app.include_router(group_router)
app.include_router(chat_router)
app.include_router(realtime_router)

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