from sqlalchemy.exc import IntegrityError
from uuid import uuid4

from src.db.agents import Agent
from src.db.groups import Group
from src.modules.group.repository import GroupRepository
from src.modules.group.schema import GroupCreate, GroupUpdate, GroupMembersAdd
from src.common.error import AppError
from src.common.constants import Status, Code
from src.modules.chat.manager import chat_manager


class GroupService:
    def __init__(self, repo: GroupRepository):
        self.repo = repo

    def create(self, data: GroupCreate) -> Group:
        group = Group(id=str(uuid4()), **data.model_dump(exclude={"agent_ids"}))
        try:
            return self.repo.create(group, data.agent_ids)
        except IntegrityError:
            raise AppError("Agent Not Found", Status.NOT_FOUND, Code.AGENT_NOT_FOUND)

    def get(self, group_id: str) -> tuple[Group, list[Agent]]:
        result = self.repo.get(group_id)
        if result is None:
            raise AppError("Group Not Found", Status.NOT_FOUND, Code.GROUP_NOT_FOUND)
        return result

    def list_all(self) -> list[Group]:
        return self.repo.list_all()

    def update(self, group_id: str, data: GroupUpdate) -> Group:
        changes = data.model_dump(exclude_unset=True)
        group = self.repo.update(group_id, changes)
        if group is None:
            raise AppError("Group Not Found", Status.NOT_FOUND, Code.GROUP_NOT_FOUND)
        chat_manager.invalidate(group_id)  # template may have changed
        return group

    def delete(self, group_id: str) -> None:
        if not self.repo.delete(group_id):
            raise AppError("Group Not Found", Status.NOT_FOUND, Code.GROUP_NOT_FOUND)
        chat_manager.invalidate(group_id)

    def add_members(self, group_id: str, data: GroupMembersAdd) -> None:
        try:
            self.repo.add_members(group_id, data.agent_ids)
        except IntegrityError:
            # SQLite doesn't say whether the group or an agent was bad; split this later if needed
            raise AppError("Group or agent not found", Status.NOT_FOUND, Code.INVALID_GROUP_OR_AGENT)
        chat_manager.invalidate(group_id)

    def remove_member(self, group_id: str, agent_id: str) -> None:
        if not self.repo.remove_member(group_id, agent_id):
            raise AppError("Agent is not in this group", Status.NOT_FOUND, Code.MEMBER_NOT_FOUND)
        chat_manager.invalidate(group_id)
