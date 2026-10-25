from fastapi import Depends
from sqlmodel import Session

from src.db.db_connection import get_session
from src.modules.chat.repository import ChatRepository
from src.modules.chat.service import ChatService
from src.modules.chat.controller import ChatController
from src.modules.chat.manager import chat_manager


def get_controller(session: Session = Depends(get_session)) -> ChatController:
    repo = ChatRepository(session)
    service = ChatService(repo, chat_manager)
    return ChatController(service)
