from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from src.db.providers import ProviderKey

def validate_http_url(v: str | None) -> str | None:
    if v and not v.startswith(("http://", "https://")):
        raise ValueError("must start with http:// or https://")
    return v

class ProviderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    provider_key: ProviderKey
    api_key: str = Field(min_length=1)
    base_url: str | None = None

    @field_validator("base_url")
    @classmethod
    def check_base_url(cls, v: str | None) -> str | None:
        return validate_http_url(v)


class ProviderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    api_key: str | None = Field(default=None, min_length=1)
    base_url: str | None = None

    @field_validator("base_url")
    @classmethod
    def check_base_url(cls, v: str | None) -> str | None:
        return validate_http_url(v)


class ProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    provider_key: ProviderKey
    base_url: str | None
    created_at: datetime


class ProviderList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    provider_key: ProviderKey
    created_at: datetime