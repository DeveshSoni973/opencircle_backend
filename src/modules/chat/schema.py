from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from src.db.messages import SenderType


class ChatSend(BaseModel):
    content: str = Field(min_length=1)


class ChatMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sender_type: SenderType
    agent_id: str | None
    content: str
    created_at: datetime
