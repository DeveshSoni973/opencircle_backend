from typing import Literal
from pydantic import BaseModel, Field


class SocketSend(BaseModel):
    """Client → server over the WebSocket: {"type": "send", "group_id": "...", "content": "..."}"""
    type: Literal["send"]
    group_id: str
    content: str = Field(min_length=1)
