from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

def skip_duplicates(ids: list[str]) -> list[str]:
    return list(set(ids))


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    system_prompt: str | None = None
    agent_ids: list[str] = []

    @field_validator("agent_ids")
    @classmethod
    def check_agent_ids(cls, v: list[str]) -> list[str]:
        return skip_duplicates(v)


class GroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    system_prompt: str | None = None


class GroupMembersAdd(BaseModel):
    agent_ids: list[str] = Field(min_length=1)

    @field_validator("agent_ids")
    @classmethod
    def check_agent_ids(cls, v: list[str]) -> list[str]:
        return skip_duplicates(v)


class GroupAgent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    avatar: str | None


class GroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    system_prompt: str | None
    created_at: datetime
    agents: list[GroupAgent]


class GroupList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
