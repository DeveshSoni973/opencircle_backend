from sqlmodel import Field
from .base import BaseTable
from enum import Enum

class SenderType(str, Enum):
    USER = "user"
    AGENT = "agent"

class Message(BaseTable, table=True):
    __tablename__ = "messages"

    group_id: str = Field(foreign_key="groups.id")
    sender_type: SenderType
    agent_id: str | None = Field(default=None, foreign_key="agents.id")
    content: str
    is_silent: bool = Field(default=False)


