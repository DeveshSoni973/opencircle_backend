from fastapi import Depends
from sqlmodel import Session

from src.db.db_connection import get_session
from src.modules.agent.repository import AgentRepository
from src.modules.agent.service import AgentService
from src.modules.agent.controller import AgentController


def get_controller(session: Session = Depends(get_session)) -> AgentController:
    repo = AgentRepository(session)
    service = AgentService(repo)
    return AgentController(service)
