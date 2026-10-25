from src.modules.chat.schema import ChatMessage, ChatSend
from src.modules.chat.service import ChatService


class ChatController:
    def __init__(self, service: ChatService):
        self.service = service

    async def send(self, group_id: str, data: ChatSend) -> ChatMessage:
        return await self.service.send(group_id, data.content)

    def list_messages(self, group_id: str) -> list[ChatMessage]:
        messages = self.service.list_messages(group_id)
        return [ChatMessage.model_validate(m) for m in messages]
