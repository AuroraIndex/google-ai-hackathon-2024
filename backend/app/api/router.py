from fastapi import WebSocket, APIRouter

from app.core.websocket import WebSocketSession

router = APIRouter()

@router.websocket("/ws")
async def generate_dashboard(websocket: WebSocket):
    wss = WebSocketSession(websocket)
    await wss.accept_connection()
    await wss.listen_and_serve()
    await wss.handle_disconnect()