from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.db.db_connection import get_session


from .controller import ProviderController
from .repository import ProviderRepository
from .schema import ProviderCreate, ProviderRead, ProviderUpdate
from .service import ProviderService
from .validator import ProviderValidator

router= APIRouter(prefix="/providers", tags=["providrs"])

def get_controller(session: Session=Depends(get_session))-> ProviderController:
    repo = ProviderRepository(session)
    service = ProviderService(repo)
    validator = ProviderValidator(repo)
    return ProviderController(service, validator)


@router.get("")
def list_providers(controller: ProviderController=Depends(get_controller))->list[ProviderRead]:
    controller.list()

@router.post("")
def create_provider(data: ProviderCreate, controller: ProviderController = Depends(get_controller)) -> ProviderRead:
  return controller.create(data)

@router.get("/{provider_id}")
def get_provider(provider_id: str, controller: ProviderController = Depends(get_controller)) -> ProviderRead:
  return controller.get(provider_id)


@router.patch("/{provider_id}")
def update_provider(provider_id: str, data: ProviderUpdate, controller: ProviderController = Depends(get_controller)) -> ProviderRead:
  return controller.update(provider_id, data)


@router.delete("/{provider_id}")
def delete_provider(provider_id: str, controller: ProviderController = Depends(get_controller)) -> None:
  controller.delete(provider_id)