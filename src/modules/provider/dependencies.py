from fastapi import Depends
from sqlmodel import Session

from src.db.db_connection import get_session  # your existing session dependency
from src.modules.provider.repository import ProviderRepository
from src.modules.provider.service import ProviderService
from src.modules.provider.controller import ProviderController


def get_controller(session: Session = Depends(get_session)) -> ProviderController:
    repo = ProviderRepository(session)
    service = ProviderService(repo)
    return ProviderController(service)