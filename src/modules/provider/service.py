import uuid

from src.common.constants import Code, Status
from src.common.error import AppError
from src.db.providers import Provider

from .repository import ProviderRepository
from .schema import ProviderCreate, ProviderUpdate


class ProviderService:
  def __init__(self, repo: ProviderRepository):
    self.repo = repo

  def _get_or_404(self, provider_id: str) -> Provider:
    provider = self.repo.get(provider_id)
    if not provider:
      raise AppError("Provider not found", Status.NOT_FOUND, Code.PROVIDER_NOT_FOUND)
    return provider

  def list(self) -> list[Provider]:
    return self.repo.list()

  def get(self, provider_id: str) -> Provider:
    return self._get_or_404(provider_id)

  def create(self, data: ProviderCreate) -> Provider:
    provider = Provider(
      id=str(uuid.uuid4()),
      name=data.name,
      provider_key=data.provider_key.value,
      api_key=data.api_key,
      base_url=data.base_url,
    )
    return self.repo.save(provider)

  def update(self, provider_id: str, data: ProviderUpdate) -> Provider:
    provider = self._get_or_404(provider_id)
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
      if field in ("name", "api_key") and value is None:
        continue  # these can't be cleared
      setattr(provider, field, value)
    return self.repo.save(provider)

  def delete(self, provider_id: str) -> None:
    provider = self._get_or_404(provider_id)
    self.repo.delete(provider)