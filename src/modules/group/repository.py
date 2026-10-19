from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select
from src.db.agents import Agent
from src.db.group_members import GroupMember
from src.db.groups import Group


class GroupRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, group: Group, agent_ids: list[str]) -> Group:
        try:
            self.session.add(group)
            self.session.flush()  # group row must exist before its members are inserted
            self.session.add_all(GroupMember(group_id=group.id, agent_id=a) for a in agent_ids)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(group)
        return group

    def get(self, group_id: str) -> tuple[Group, list[Agent]] | None:
        group = self.session.get(Group, group_id)
        if group is None:
            return None
        agents = self.session.exec(
            select(Agent)
            .join(GroupMember, col(GroupMember.agent_id) == Agent.id)
            .where(GroupMember.group_id == group_id)
        ).all()
        return group, list(agents)

    def list_all(self) -> list[Group]:
        return list(self.session.exec(select(Group)).all())

    def update(self, group_id: str, data: dict) -> Group | None:
        group = self.session.get(Group, group_id)
        if group is None:
            return None
        group.sqlmodel_update(data)
        self.session.commit()
        self.session.refresh(group)
        return group

    def delete(self, group_id: str) -> bool:
        group = self.session.get(Group, group_id)
        if group is None:
            return False
        self.session.delete(group)
        self.session.commit()
        return True

    def add_members(self, group_id: str, agent_ids: list[str]) -> None:
        existing = set(self.session.exec(
            select(GroupMember.agent_id).where(GroupMember.group_id == group_id)
        ).all())
        new_ids = [a for a in agent_ids if a not in existing]
        try:
            self.session.add_all(GroupMember(group_id=group_id, agent_id=a) for a in new_ids)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise

    def remove_member(self, group_id: str, agent_id: str) -> bool:
        member = self.session.get(GroupMember, (group_id, agent_id))
        if member is None:
            return False
        self.session.delete(member)
        self.session.commit()
        return True
