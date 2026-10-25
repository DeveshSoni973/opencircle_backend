from fastapi import APIRouter, Depends

from src.modules.chat.controller import ChatController
from src.modules.chat.dependencies import get_controller
from src.modules.chat.schema import ChatSend, ChatMessage

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{group_id}", status_code=202)
async def send_message(group_id: str, data: ChatSend, controller: ChatController = Depends(get_controller)) -> ChatMessage:
    # same as sending over the socket; replies arrive on /realtime/ws
    return await controller.send(group_id, data)


@router.get("/{group_id}")
def list_messages(group_id: str, controller: ChatController = Depends(get_controller)) -> list[ChatMessage]:
    return controller.list_messages(group_id)
