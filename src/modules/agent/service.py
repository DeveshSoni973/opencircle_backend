from sqlalchemy.exc import IntegrityError
from uuid import uuid4

from src.db.agents import Agent
from src.modules.agent.repository import AgentRepository
from src.modules.agent.schema import AgentCreate, AgentUpdate
from src.common.error import AppError
from src.common.constants import Status, Code


class AgentService:
    def __init__(self, repo: AgentRepository):
        self.repo = repo

    def create(self, data: AgentCreate) -> Agent:
        agent = Agent(id=str(uuid4()), **data.model_dump())
        try:
            return self.repo.create(agent)
        except IntegrityError:
            raise AppError("Provider Not Found", Status.NOT_FOUND, Code.PROVIDER_NOT_FOUND)

    def get(self, agent_id: str) -> Agent:
        agent = self.repo.get(agent_id)
        if agent is None:
            raise AppError("Agent Not Found", Status.NOT_FOUND, Code.AGENT_NOT_FOUND)
        return agent

    def list_all(self) -> list[Agent]:
        return self.repo.list_all()

    def update(self, agent_id: str, data: AgentUpdate) -> Agent:
        changes = data.model_dump(exclude_unset=True)
        try:
            agent = self.repo.update(agent_id, changes)
        except IntegrityError:
            raise AppError("Provider Not Found", Status.NOT_FOUND, Code.PROVIDER_NOT_FOUND)
        if agent is None:
            raise AppError("Agent Not Found", Status.NOT_FOUND, Code.AGENT_NOT_FOUND)
        return agent

    def delete(self, agent_id: str) -> None:
        if not self.repo.delete(agent_id):
            raise AppError("Agent Not Found", Status.NOT_FOUND, Code.AGENT_NOT_FOUND)
