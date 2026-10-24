import logging
from uuid import uuid4

from opencircle_module import Agent as ModuleAgent
from opencircle_module import GroupChat
from opencircle_module import Message as ModuleMessage

from src.common.constants import Code, Status
from src.common.encryption_decryption import decrypt
from src.common.error import AppError
from src.db.messages import Message, SenderType
from src.modules.chat.repository import ChatRepository

logger = logging.getLogger(__name__)

USER_SENDER = "usr"  # the module's sender id for the human user
SILENT = "[SILENT]"


class ChatService:
    def __init__(self, repo: ChatRepository):
        self.repo = repo

    def _require_group(self, group_id: str) -> None:
        if self.repo.get_group(group_id) is None:
            raise AppError("Group Not Found", Status.NOT_FOUND, Code.GROUP_NOT_FOUND)

    def list_messages(self, group_id: str) -> list[Message]:
        self._require_group(group_id)
        return self.repo.list_messages(group_id)  # silent turns stay in the table, hidden from users

    async def send(self, group_id: str, content: str) -> list[Message]:
        self._require_group(group_id)
        rows = self.repo.get_group_agents(group_id)
        if not rows:
            raise AppError("Group has no agents", Status.BAD_REQUEST, Code.GROUP_HAS_NO_AGENTS)

        # history is read before the new user message is saved; chat.run() appends the query itself
        previous = self.repo.list_messages(group_id)

        user_msg = Message(id=str(uuid4()), group_id=group_id, sender_type=SenderType.USER, content=content)
        self.repo.add_messages([user_msg])

        agents = []
        for agent, provider in rows:
            module_agent = ModuleAgent(
                name=agent.name,
                model=agent.model,
                provider=provider.provider_key.value,
                api_key=decrypt(provider.api_encrypted),
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
                max_rounds=agent.max_rounds,
            )
            module_agent.agent_id = agent.id  # so replies map straight onto messages.agent_id
            agents.append(module_agent)

        turns: list[Message] = []

        def on_turn(module_agent: ModuleAgent, response: str | None) -> None:
            # fires once per agent turn, silent or not, so every turn becomes a row
            silent = response is None
            turns.append(Message(
                id=str(uuid4()),
                group_id=group_id,
                sender_type=SenderType.AGENT,
                agent_id=module_agent.agent_id,
                content=SILENT if silent else response,
                is_silent=silent,
            ))

        chat = GroupChat(
            agents=agents,
            max_rounds=max(a.max_rounds for a in agents),
            on_round_complete=on_turn,
        )
        chat.history = [
            ModuleMessage(
                sender_id=USER_SENDER if m.sender_type == SenderType.USER else m.agent_id,
                content=m.content,
                msg_id=m.id,
            )
            for m in previous
        ]

        try:
            await chat.run(content)
        except Exception:
            logger.exception("Chat run failed for group %s", group_id)
            raise AppError("Chat run failed", Status.UPSTREAM_FAILED, Code.CHAT_RUN_FAILED)
        finally:
            if turns:
                self.repo.add_messages(turns)

        return [user_msg, *(t for t in turns if not t.is_silent)]
