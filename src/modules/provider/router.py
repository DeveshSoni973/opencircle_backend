from fastapi import APIRouter, Depends

from src.modules.provider.controller import ProviderController
from src.modules.provider.dependencies import get_controller
from src.modules.provider.schema import (
    ProviderCreate,
    ProviderUpdate,
    ProviderRead,
    ProviderList,
)

router = APIRouter(prefix="/providers", tags=["providers"])


@router.post("", status_code=201)
def create_provider(data: ProviderCreate, controller: ProviderController = Depends(get_controller)) -> ProviderRead:
    return controller.create(data)


@router.get("")
def list_providers(controller: ProviderController = Depends(get_controller)) -> list[ProviderList]:
    return controller.list_all()


@router.get("/{provider_id}")
def get_provider(provider_id: str, controller: ProviderController = Depends(get_controller)) -> ProviderRead:
    return controller.get(provider_id)


@router.patch("/{provider_id}")
def update_provider(provider_id: str, data: ProviderUpdate, controller: ProviderController = Depends(get_controller)) -> ProviderRead:
    return controller.update(provider_id, data)


@router.delete("/{provider_id}", status_code=204)
def delete_provider(provider_id: str, controller: ProviderController = Depends(get_controller)) -> None:
    controller.delete(provider_id)