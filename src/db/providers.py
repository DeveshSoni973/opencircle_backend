from enum import Enum
from sqlmodel import Field
from src.db.base import BaseTable

class ProviderKey(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    GOOGLE = "google"
    NVIDIA = "nvidia"
    OPENROUTER = "openrouter"

class Provider(BaseTable, table=True):
    __tablename__ = "providers"

    name: str
    provider_key: ProviderKey 
    api_key: str
    base_url: str | None = Field(default=None)
