from src.common.constants import Code, Status
from src.common.error import AppError
from src.db.messages import Message
from src.modules.chat.manager import ChatManager
from src.modules.chat.repository import ChatRepository
from src.modules.chat.schema import ChatMessage


class ChatService:
    def __init__(self, repo: ChatRepository, manager: ChatManager):
        self.repo = repo
        self.manager = manager

    def list_messages(self, group_id: str) -> list[Message]:
        if self.repo.get_group(group_id) is None:
            raise AppError("Group Not Found", Status.NOT_FOUND, Code.GROUP_NOT_FOUND)
        return self.repo.list_messages(group_id)  # silent/error turns stay in the table, hidden from users

    async def send(self, group_id: str, content: str) -> ChatMessage:
        # replies are not returned here; they stream over /realtime/ws as each agent finishes
        return await self.manager.send(group_id, content)
