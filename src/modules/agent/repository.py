from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from src.db.agents import Agent


class AgentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, agent: Agent) -> Agent:
        try:
            self.session.add(agent)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(agent)
        return agent

    def get(self, agent_id: str) -> Agent | None:
        return self.session.get(Agent, agent_id)

    def list_all(self) -> list[Agent]:
        return list(self.session.exec(select(Agent)).all())

    def update(self, agent_id: str, data: dict) -> Agent | None:
        agent = self.session.get(Agent, agent_id)
        if agent is None:
            return None
        try:
            agent.sqlmodel_update(data)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(agent)
        return agent

    def delete(self, agent_id: str) -> bool:
        agent = self.session.get(Agent, agent_id)
        if agent is None:
            return False
        self.session.delete(agent)
        self.session.commit()
        return True
