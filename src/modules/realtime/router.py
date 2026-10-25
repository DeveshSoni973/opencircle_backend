import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from src.common.error import AppError
from src.modules.chat.manager import chat_manager
from src.common.broker import broker
from src.modules.realtime.schema import SocketSend

router = APIRouter(prefix="/realtime", tags=["realtime"])


@router.websocket("/ws")
async def realtime_socket(ws: WebSocket) -> None:
    """One connection for the whole app; every event carries its group_id.

    client → server:  {"type": "send", "group_id": "...", "content": "..."}
    server → client:  user_message | agent_message | run_done | error
    """
    await ws.accept()
    queue = broker.subscribe()

    async def forward_events() -> None:  # the only writer to this socket
        while True:
            await ws.send_json(await queue.get())

    forwarder = asyncio.create_task(forward_events())
    try:
        while True:
            raw = await ws.receive_text()
            try:
                cmd = SocketSend.model_validate(json.loads(raw))
                await chat_manager.send(cmd.group_id, cmd.content)
            except (json.JSONDecodeError, ValidationError):
                queue.put_nowait({"type": "error", "code": "invalid_message",
                                  "message": 'expected {"type": "send", "group_id": "...", "content": "..."}'})
            except AppError as e:
                queue.put_nowait({"type": "error", "group_id": cmd.group_id, "code": e.code, "message": e.message})
    except WebSocketDisconnect:
        pass
    finally:
        forwarder.cancel()
        broker.unsubscribe(queue)
