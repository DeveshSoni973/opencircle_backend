from sqlmodel import Field
from .base import BaseTable

class Group(BaseTable, table=True):
    __tablename__ = "groups"

    name: str
    description: str | None = Field(default=None)
    system_prompt: str | None = Field(default=None)
