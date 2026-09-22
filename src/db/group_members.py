from sqlmodel import Field, SQLModel

class GroupMember(SQLModel, table=True):
    __tablename__ = "group_members"

    group_id: str = Field(foreign_key="groups.id", primary_key=True)
    agent_id: str = Field(foreign_key="agents.id", primary_key=True)
