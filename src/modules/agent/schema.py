from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    avatar: str | None = None
    provider_id: str
    model: str = Field(min_length=1)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, gt=0)
    max_rounds: int = Field(default=5, ge=1)
    system_prompt: str | None = None

class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    avatar: str | None = None
    provider_id: str | None = None
    model: str | None = Field(default=None, min_length=1)
    temperature: float | None = Field(default=None, ge=0, le=2)
    max_tokens: int | None = Field(default=None, gt=0)
    max_rounds: int | None = Field(default=None, ge=1)
    system_prompt: str | None = None

class AgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    avatar: str | None
    provider_id: str
    model: str
    temperature: float
    max_tokens: int
    max_rounds: int
    system_prompt: str | None
    created_at: datetime

class AgentList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    avatar: str | None
    provider_id: str
    model: str