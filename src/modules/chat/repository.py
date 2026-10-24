from sqlmodel import Session, col, select
from src.db.agents import Agent
from src.db.group_members import GroupMember
from src.db.groups import Group
from src.db.messages import Message
from src.db.providers import Provider


class ChatRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_group(self, group_id: str) -> Group | None:
        return self.session.get(Group, group_id)

    def get_group_agents(self, group_id: str) -> list[tuple[Agent, Provider]]:
        rows = self.session.exec(
            select(Agent, Provider)
            .join(GroupMember, col(GroupMember.agent_id) == Agent.id)
            .join(Provider, col(Provider.id) == Agent.provider_id)
            .where(GroupMember.group_id == group_id)
        ).all()
        return list(rows)

    def list_messages(self, group_id: str, include_silent: bool = False) -> list[Message]:
        query = select(Message).where(Message.group_id == group_id)
        if not include_silent:
            query = query.where(col(Message.is_silent).is_(False))
        return list(self.session.exec(query.order_by(col(Message.created_at))).all())

    def add_messages(self, messages: list[Message]) -> None:
        self.session.add_all(messages)
        self.session.commit()
