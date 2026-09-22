from sqlmodel import Field
from .base import BaseTable

class Agent(BaseTable, table=True):
    __tablename__ = "agents"

    name: str
    avatar: str
    provider_id: str = Field(foreign_key="providers.id")
    model: str
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1024)
    max_rounds: int = Field(default=5)
    system_prompt: str | None = Field(default=None)
