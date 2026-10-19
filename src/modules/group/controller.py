from src.modules.group.service import GroupService
from src.modules.group.schema import (
    GroupCreate,
    GroupUpdate,
    GroupMembersAdd,
    GroupRead,
    GroupList,
    GroupAgent,
)


class GroupController:
    def __init__(self, service: GroupService):
        self.service = service

    def create(self, data: GroupCreate) -> GroupList:
        group = self.service.create(data)
        return GroupList.model_validate(group)

    def get(self, group_id: str) -> GroupRead:
        group, agents = self.service.get(group_id)
        return GroupRead(
            **group.model_dump(),
            agents=[GroupAgent.model_validate(a) for a in agents],
        )

    def list_all(self) -> list[GroupList]:
        groups = self.service.list_all()
        return [GroupList.model_validate(g) for g in groups]

    def update(self, group_id: str, data: GroupUpdate) -> GroupList:
        group = self.service.update(group_id, data)
        return GroupList.model_validate(group)

    def delete(self, group_id: str) -> None:
        self.service.delete(group_id)

    def add_members(self, group_id: str, data: GroupMembersAdd) -> None:
        self.service.add_members(group_id, data)

    def remove_member(self, group_id: str, agent_id: str) -> None:
        self.service.remove_member(group_id, agent_id)
