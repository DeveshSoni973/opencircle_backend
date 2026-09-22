from datetime import datetime
from sqlmodel import Field, SQLModel

class BaseTable(SQLModel):
    id: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: datetime | None = Field(default=None)
