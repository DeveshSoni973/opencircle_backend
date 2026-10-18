from sqlmodel import Session, select
from src.db.providers import Provider

class ProviderRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, provider: Provider) -> Provider:
        self.session.add(provider)
        self.session.commit()
        self.session.refresh(provider)
        return provider

    def get(self, provider_id: str) -> Provider | None:
        return self.session.get(Provider, provider_id)

    def list_all(self) -> list[Provider]:
        return list(self.session.exec(select(Provider)).all())

    def update(self, provider_id: str, data: dict) -> Provider | None:
        provider = self.session.get(Provider, provider_id)
        if provider is None:
            return None
        provider.sqlmodel_update(data)
        self.session.commit()
        self.session.refresh(provider)
        return provider

    def delete(self, provider_id: str) -> bool:
        provider = self.session.get(Provider, provider_id)
        if provider is None:
            return False
        self.session.delete(provider)
        self.session.commit()
        return True