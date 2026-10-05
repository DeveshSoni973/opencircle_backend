from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from src.db.providers import Provider


class ProviderKey(str, Enum):
  openai = "openai"
  anthropic = "anthropic"
  groq = "groq"
  google = "google"
  nvidia = "nvidia"
  openrouter = "openrouter"


class ProviderCreate(BaseModel):
  name: str = Field(min_length=1, max_length=100)
  provider_key: ProviderKey
  api_key: str = Field(min_length=1)
  base_url: str | None = None


class ProviderUpdate(BaseModel):
  name: str | None = Field(default=None, min_length=1, max_length=100)
  api_key: str | None = Field(default=None, min_length=1)
  base_url: str | None = None


class ProviderRead(BaseModel):
  id: str
  name: str
  provider_key: str
  base_url: str | None
  api_key_masked: str
  created_at: datetime

  @classmethod
  def from_model(cls, p: Provider) -> "ProviderRead":
    key = p.api_key
    masked = f"{key[:3]}...{key[-4:]}" if len(key) > 8 else "****"
    return cls(
      id=p.id,
      name=p.name,
      provider_key=p.provider_key,
      base_url=p.base_url,
      api_key_masked=masked,
      created_at=p.created_at,
    )