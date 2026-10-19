from fastapi import APIRouter, Depends

from src.modules.agent.controller import AgentController
from src.modules.agent.dependencies import get_controller
from src.modules.agent.schema import (
    AgentCreate,
    AgentUpdate,
    AgentRead,
    AgentList,
)

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", status_code=201)
def create_agent(data: AgentCreate, controller: AgentController = Depends(get_controller)) -> AgentRead:
    return controller.create(data)


@router.get("")
def list_agents(controller: AgentController = Depends(get_controller)) -> list[AgentList]:
    return controller.list_all()


@router.get("/{agent_id}")
def get_agent(agent_id: str, controller: AgentController = Depends(get_controller)) -> AgentRead:
    return controller.get(agent_id)


@router.patch("/{agent_id}")
def update_agent(agent_id: str, data: AgentUpdate, controller: AgentController = Depends(get_controller)) -> AgentRead:
    return controller.update(agent_id, data)


@router.delete("/{agent_id}", status_code=204)
def delete_agent(agent_id: str, controller: AgentController = Depends(get_controller)) -> None:
    controller.delete(agent_id)
