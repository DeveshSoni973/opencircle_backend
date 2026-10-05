from .schema import ProviderCreate, ProviderRead, ProviderUpdate
from .service import ProviderService
from .validator import ProviderValidator


class ProviderController:
  def __init__(self, service: ProviderService, validator: ProviderValidator):
    self.service = service
    self.validator = validator

  def list(self) -> list[ProviderRead]:
    providers = self.service.list()
    return [ProviderRead.from_model(p) for p in providers]

  def get(self, provider_id: str) -> ProviderRead:
    provider = self.service.get(provider_id)
    return ProviderRead.from_model(provider)

  def create(self, data: ProviderCreate) -> ProviderRead:
    self.validator.validate_base_url(data.base_url)   # 1. check the rules
    provider = self.service.create(data)              # 2. do the work
    return ProviderRead.from_model(provider)          # 3. shape the reply

  def update(self, provider_id: str, data: ProviderUpdate) -> ProviderRead:
    if "base_url" in data.model_fields_set:           # only check if the caller sent it
      self.validator.validate_base_url(data.base_url)
    provider = self.service.update(provider_id, data)
    return ProviderRead.from_model(provider)

  def delete(self, provider_id: str) -> None:
    self.validator.ensure_not_in_use(provider_id)     # block if agents still use it
    self.service.delete(provider_id)