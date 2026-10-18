from src.modules.provider.repository import ProviderRepository
from src.db.providers import Provider
from src.modules.provider.schema import ProviderCreate, ProviderUpdate
from src.common.encryption_decryption import encrypt
from src.common.error import AppError
from src.common.constants import Status, Code

class ProviderService:
    def __init__(self, repo: ProviderRepository):
        self.repo = repo

    def create(self, data: ProviderCreate) -> Provider:
        provider_data = data.model_dump()
        provider_data["api_encrypted"] = encrypt(provider_data.pop("api_key"))
        provider = Provider(**provider_data)
        return self.repo.create(provider)

    def get(self, provider_id: str) -> Provider:
        provider=self.repo.get(provider_id)
        if provider is None:
            raise AppError("Provider Not Found", Status.NOT_FOUND, Code.PROVIDER_NOT_FOUND)
        return provider

    def list_all(self) -> list[Provider]:
        return self.repo.list_all()

    def update(self, provider_id: str, data: ProviderUpdate) -> Provider:
        changes=data.model_dump(exclude_unset=True)
        if "api_key" in changes:
            changes["api_encrypted"] = encrypt(changes.pop("api_key"))
        provider = self.repo.update(provider_id, changes)
        if provider is None:
            raise AppError("Provider Not Found", Status.NOT_FOUND, Code.PROVIDER_NOT_FOUND)
        return provider

    def delete(self, provider_id: str) -> None:
        if not self.repo.delete(provider_id):
            raise AppError("Provider Not Found", Status.NOT_FOUND, Code.PROVIDER_NOT_FOUND)