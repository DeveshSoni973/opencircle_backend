from fastapi import APIRouter, Depends

from src.modules.group.controller import GroupController
from src.modules.group.dependencies import get_controller
from src.modules.group.schema import (
    GroupCreate,
    GroupUpdate,
    GroupMembersAdd,
    GroupRead,
    GroupList,
)

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", status_code=201)
def create_group(data: GroupCreate, controller: GroupController = Depends(get_controller)) -> GroupList:
    return controller.create(data)


@router.get("")
def list_groups(controller: GroupController = Depends(get_controller)) -> list[GroupList]:
    return controller.list_all()


@router.get("/{group_id}")
def get_group(group_id: str, controller: GroupController = Depends(get_controller)) -> GroupRead:
    return controller.get(group_id)


@router.patch("/{group_id}")
def update_group(group_id: str, data: GroupUpdate, controller: GroupController = Depends(get_controller)) -> GroupList:
    return controller.update(group_id, data)


@router.delete("/{group_id}", status_code=204)
def delete_group(group_id: str, controller: GroupController = Depends(get_controller)) -> None:
    controller.delete(group_id)


@router.post("/{group_id}/agents", status_code=204)
def add_group_agents(group_id: str, data: GroupMembersAdd, controller: GroupController = Depends(get_controller)) -> None:
    controller.add_members(group_id, data)


@router.delete("/{group_id}/agents/{agent_id}", status_code=204)
def remove_group_agent(group_id: str, agent_id: str, controller: GroupController = Depends(get_controller)) -> None:
    controller.remove_member(group_id, agent_id)
