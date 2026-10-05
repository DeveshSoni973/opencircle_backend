from src.common.constants import Code, Status
from src.common.error import AppError

from .repository import ProviderRepository


class ProviderValidator:
  def __init__(self, repo: ProviderRepository):
    self.repo = repo

  def validate_base_url(self, base_url: str | None) -> None:
    if base_url and not base_url.startswith(("http://", "https://")):
      raise AppError(
        "base_url must start with http:// or https://",
        Status.BAD_REQUEST,
        Code.INVALID_BASE_URL,
      )

  def ensure_not_in_use(self, provider_id: str) -> None:
    count = self.repo.count_agents(provider_id)
    if count:
      raise AppError(
        f"Provider is used by {count} agent(s); remove or reassign them first",
        Status.CONFLICT,
        Code.PROVIDER_IN_USE,
      )