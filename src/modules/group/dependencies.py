from fastapi import Depends
from sqlmodel import Session

from src.db.db_connection import get_session
from src.modules.group.repository import GroupRepository
from src.modules.group.service import GroupService
from src.modules.group.controller import GroupController


def get_controller(session: Session = Depends(get_session)) -> GroupController:
    repo = GroupRepository(session)
    service = GroupService(repo)
    return GroupController(service)
