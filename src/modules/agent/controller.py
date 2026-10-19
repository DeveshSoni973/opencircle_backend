from src.modules.agent.service import AgentService
from src.modules.agent.schema import AgentCreate, AgentUpdate, AgentRead, AgentList


class AgentController:
    def __init__(self, service: AgentService):
        self.service = service

    def create(self, data: AgentCreate) -> AgentRead:
        agent = self.service.create(data)
        return AgentRead.model_validate(agent)

    def get(self, agent_id: str) -> AgentRead:
        agent = self.service.get(agent_id)
        return AgentRead.model_validate(agent)

    def list_all(self) -> list[AgentList]:
        agents = self.service.list_all()
        return [AgentList.model_validate(a) for a in agents]

    def update(self, agent_id: str, data: AgentUpdate) -> AgentRead:
        agent = self.service.update(agent_id, data)
        return AgentRead.model_validate(agent)

    def delete(self, agent_id: str) -> None:
        self.service.delete(agent_id)
