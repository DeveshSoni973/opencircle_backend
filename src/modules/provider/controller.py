from src.modules.provider.service import ProviderService
from src.modules.provider.schema import ProviderCreate, ProviderUpdate, ProviderRead, ProviderList


class ProviderController:
    def __init__(self, service: ProviderService):
        self.service = service

    def create(self, data: ProviderCreate) -> ProviderRead:
        provider = self.service.create(data)
        return ProviderRead.model_validate(provider)

    def get(self, provider_id: str) -> ProviderRead:
        provider = self.service.get(provider_id)
        return ProviderRead.model_validate(provider)

    def list_all(self) -> list[ProviderList]:
        providers = self.service.list_all()
        return [ProviderList.model_validate(p) for p in providers]

    def update(self, provider_id: str, data: ProviderUpdate) -> ProviderRead:
        provider = self.service.update(provider_id, data)
        return ProviderRead.model_validate(provider)

    def delete(self, provider_id: str) -> None:
        self.service.delete(provider_id)