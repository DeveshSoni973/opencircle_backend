from sqlmodel import Session, func, select

from src.db.agents import Agent
from src.db.providers import Provider


class ProviderRepository:
  def __init__(self, session: Session):
    self.session = session

  def list(self) -> list[Provider]:
    return list(self.session.exec(select(Provider).order_by(Provider.created_at)).all())

  def get(self, provider_id: str) -> Provider | None:
    return self.session.get(Provider, provider_id)

  def save(self, provider: Provider) -> Provider:
    self.session.add(provider)
    self.session.commit()
    self.session.refresh(provider)
    return provider

  def delete(self, provider: Provider) -> None:
    self.session.delete(provider)
    self.session.commit()

  def count_agents(self, provider_id: str) -> int:
    stmt = select(func.count()).select_from(Agent).where(Agent.provider_id == provider_id)
    return self.session.exec(stmt).one()