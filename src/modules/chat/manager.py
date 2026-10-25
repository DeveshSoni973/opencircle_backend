import asyncio
import logging
from uuid import uuid4

from opencircle_module import Agent as ModuleAgent
from opencircle_module import GroupChat, TurnResult, TurnStatus
from opencircle_module import Message as ModuleMessage
from sqlmodel import Session

from src.common.constants import Code, Status
from src.common.encryption_decryption import decrypt
from src.common.error import AppError
from src.db.db_connection import engine
from src.db.messages import Message, SenderType
from src.modules.chat.repository import ChatRepository
from src.modules.chat.schema import ChatMessage
from src.common.broker import Broker, broker

logger = logging.getLogger(__name__)

USER_SENDER = "usr"  # the module's sender id for the human user
SILENT = "[SILENT]"
ERROR_PREFIX = "[ERROR]"  # failed turns are stored hidden, like silent ones, with the error text


class ChatManager:
    """Keeps one live GroupChat per group; the module does the conversation work.

    - first message for a group (or after a restart/edit): build the chat from the DB once
    - every message: chat.run(message); mid-run, the module adds it to the run already going
    - every turn: save to the DB immediately, then publish to the broker
    """

    def __init__(self, broker: Broker):
        self.broker = broker
        self._chats: dict[str, GroupChat] = {}
        self._runs: dict[str, asyncio.Task] = {}   # the run that owns each group's loop
        self._joining: set[asyncio.Task] = set()   # run() calls made mid-run; kept so they aren't garbage-collected
        self._stale: set[str] = set()  # edited while running: rebuild once the run ends

    async def send(self, group_id: str, content: str) -> ChatMessage:
        chat = self._chats.get(group_id) or self._build(group_id)  # history loaded before the new message is saved

        user_msg = self._save(Message(id=str(uuid4()), group_id=group_id, sender_type=SenderType.USER, content=content))
        self.broker.publish({"type": "user_message", "group_id": group_id, "message": user_msg.model_dump(mode="json")})

        if group_id in self._runs:
            # mid-run: the module adds it to the running loop (agents mid-reply finish, the rest are invoked)
            task = asyncio.create_task(chat.run(content))
            self._joining.add(task)
            task.add_done_callback(self._joining.discard)
        else:
            self._runs[group_id] = asyncio.create_task(self._run(group_id, chat, content))
        return user_msg

    def invalidate(self, group_id: str) -> None:
        """Group, its members or its template changed: rebuild from the DB on the next message."""
        if group_id in self._runs:
            self._stale.add(group_id)  # don't swap the chat mid-run, or two runs would overlap
        else:
            self._chats.pop(group_id, None)

    def invalidate_all(self) -> None:
        """An agent or provider changed; agents are shared across groups, so rebuild them all."""
        for group_id in list(self._chats):
            self.invalidate(group_id)

    async def shutdown(self) -> None:
        tasks = [*self._runs.values(), *self._joining]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _run(self, group_id: str, chat: GroupChat, content: str) -> None:
        try:
            await chat.run(content)
        except Exception:
            logger.exception("Chat run failed for group %s", group_id)
            self.broker.publish({"type": "error", "group_id": group_id, "code": Code.CHAT_RUN_FAILED, "message": "Chat run failed"})
        finally:
            self._runs.pop(group_id, None)
            if group_id in self._stale:
                self._stale.discard(group_id)
                self._chats.pop(group_id, None)
            self.broker.publish({"type": "run_done", "group_id": group_id})

    def _build(self, group_id: str) -> GroupChat:
        with Session(engine) as session:
            repo = ChatRepository(session)
            group = repo.get_group(group_id)
            if group is None:
                raise AppError("Group Not Found", Status.NOT_FOUND, Code.GROUP_NOT_FOUND)
            rows = repo.get_group_agents(group_id)
            if not rows:
                raise AppError("Group has no agents", Status.BAD_REQUEST, Code.GROUP_HAS_NO_AGENTS)

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
            chat = GroupChat(
                agents=agents,
                system_prompt=group.system_prompt or "default",  # template name: default / debate / creative / technical
                on_round_complete=lambda agent, result: self._on_turn(group_id, agent, result),
            )
            chat.history = [
                ModuleMessage(
                    sender_id=USER_SENDER if m.sender_type == SenderType.USER else m.agent_id,
                    content=m.content,
                    msg_id=m.id,
                )
                for m in repo.list_messages(group_id)  # silent/error rows are excluded
            ]

        self._chats[group_id] = chat
        return chat

    def _on_turn(self, group_id: str, agent: ModuleAgent, result: TurnResult) -> None:
        # fires once per agent turn, spoke / silent / error; saved before it is published
        if result.status == TurnStatus.SPOKE:
            text, hidden = result.content, False
        elif result.status == TurnStatus.SILENT:
            text, hidden = SILENT, True
        else:
            logger.warning("Agent %s failed in group %s: %s", agent.agent_id, group_id, result.error)
            text, hidden = f"{ERROR_PREFIX} {result.error}", True

        saved = self._save(Message(
            id=str(uuid4()),
            group_id=group_id,
            sender_type=SenderType.AGENT,
            agent_id=agent.agent_id,
            content=text,
            is_silent=hidden,
        ))
        if not hidden:  # silent/error turns stay in the DB only
            self.broker.publish({"type": "agent_message", "group_id": group_id, "message": saved.model_dump(mode="json")})

    @staticmethod
    def _save(message: Message) -> ChatMessage:
        # own short session: the live chat outlives any request's session
        with Session(engine) as session:
            ChatRepository(session).add_messages([message])
            return ChatMessage.model_validate(message)


chat_manager = ChatManager(broker)
