import logging
from uuid import uuid4

from opencircle_module import Agent as ModuleAgent
from opencircle_module import GroupChat, TurnResult, TurnStatus
from opencircle_module import Message as ModuleMessage

from src.common.constants import Code, Status
from src.common.encryption_decryption import decrypt
from src.common.error import AppError
from src.db.groups import Group
from src.db.messages import Message, SenderType
from src.modules.chat.repository import ChatRepository

logger = logging.getLogger(__name__)

USER_SENDER = "usr"  # the module's sender id for the human user
SILENT = "[SILENT]"
ERROR_PREFIX = "[ERROR]"  # failed turns are stored hidden, like silent ones, with the error text


class ChatService:
    def __init__(self, repo: ChatRepository):
        self.repo = repo

    def _require_group(self, group_id: str) -> Group:
        group = self.repo.get_group(group_id)
        if group is None:
            raise AppError("Group Not Found", Status.NOT_FOUND, Code.GROUP_NOT_FOUND)
        return group

    def list_messages(self, group_id: str) -> list[Message]:
        self._require_group(group_id)
        return self.repo.list_messages(group_id)  # silent turns stay in the table, hidden from users

    async def send(self, group_id: str, content: str) -> list[Message]:
        group = self._require_group(group_id)
        rows = self.repo.get_group_agents(group_id)
        if not rows:
            raise AppError("Group has no agents", Status.BAD_REQUEST, Code.GROUP_HAS_NO_AGENTS)

        # history is read before the new user message is saved; chat.run() appends the query itself
        previous = self.repo.list_messages(group_id)

        user_msg = Message(id=str(uuid4()), group_id=group_id, sender_type=SenderType.USER, content=content)
        self.repo.add_messages([user_msg])

        agents = [
            ModuleAgent(
                agent_id=agent.id,  # replies map straight onto messages.agent_id
                name=agent.name,
                model=agent.model,
                provider=provider.provider_key.value,
                api_key=decrypt(provider.api_encrypted),
                base_url=provider.base_url,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
                max_rounds=agent.max_rounds,
            )
            for agent, provider in rows
        ]

        turns: list[Message] = []

        def on_turn(module_agent: ModuleAgent, result: TurnResult) -> None:
            # fires once per agent turn, spoke / silent / error, so every turn becomes a row
            if result.status == TurnStatus.SPOKE:
                text, hidden = result.content, False
            elif result.status == TurnStatus.SILENT:
                text, hidden = SILENT, True
            else:
                logger.warning("Agent %s failed in group %s: %s", module_agent.agent_id, group_id, result.error)
                text, hidden = f"{ERROR_PREFIX} {result.error}", True
            turns.append(Message(
                id=str(uuid4()),
                group_id=group_id,
                sender_type=SenderType.AGENT,
                agent_id=module_agent.agent_id,
                content=text,
                is_silent=hidden,
            ))

        chat = GroupChat(
            agents=agents,
            system_prompt=group.system_prompt or "default",  # template name: default / debate / creative / technical
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
