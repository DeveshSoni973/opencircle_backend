"""Test setup: throwaway SQLite DB and a fake LLM, so tests never touch opencircle.db or real APIs."""
import asyncio
import os
import tempfile

from cryptography.fernet import Fernet

# must be set before anything imports src (the engine is created at import time)
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(tempfile.mkdtemp(), 'test.db')}"
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from opencircle_module.providers.base import BaseProvider  # noqa: E402
from opencircle_module.providers.factory import ProviderFactory  # noqa: E402

from src.db.db_connection import engine  # noqa: E402
from src.main import app  # noqa: E402

engine.echo = False


class FakeLLM(BaseProvider):
    """The agent's model name picks its behaviour."""

    def __init__(self, api_key=None, base_url=None):
        super().__init__(api_key)

    async def chat(self, model, messages, **kwargs):
        latest = [m["content"] for m in messages if m["role"] == "user"][-1]
        topic = "Korea" if "Korea" in latest else "Japan" if "Japan" in latest else "chat"
        if model == "fast":
            return f"fast: {topic}"
        if model == "slow":
            await asyncio.sleep(0.4)
            return f"slow: {topic}"
        if model == "quiet":
            return "[SILENT]"
        if model == "doner":
            return "all good [DONE]"
        raise RuntimeError("upstream 401")

    def sync_chat(self, *args, **kwargs):
        raise NotImplementedError


ProviderFactory._providers["openai"] = FakeLLM  # the backend's "openai" provider key now hits FakeLLM


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def make_group(client):
    """make_group("fast", "slow") -> (group_id, {model: agent_id})"""
    provider_id = client.post("/providers", json={"name": "p", "provider_key": "openai", "api_key": "k"}).json()["id"]

    def _make(*models: str, max_rounds: int = 1):
        agent_ids = {}
        for model in models:
            r = client.post("/agents", json={"name": model, "provider_id": provider_id, "model": model, "max_rounds": max_rounds})
            agent_ids[model] = r.json()["id"]
        group_id = client.post("/groups", json={"name": "g", "agent_ids": list(agent_ids.values())}).json()["id"]
        return group_id, agent_ids

    return _make


def collect_until_run_done(ws, group_id, limit=50):
    """Read socket events for this group until its run_done."""
    events = []
    for _ in range(limit):
        event = ws.receive_json()
        if event.get("group_id") != group_id:
            continue
        events.append(event)
        if event["type"] == "run_done":
            return events
    raise AssertionError(f"no run_done within {limit} events: {events}")
