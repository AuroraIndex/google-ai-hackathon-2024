from fastapi import WebSocket, APIRouter, WebSocketException, WebSocketDisconnect
from typing import List

from app.core.genai.gemini_wrapper import start_gemini_session
from app.core.websocket import WebSocketSession

router = APIRouter()

@router.websocket("/ws")
async def generate_dashboard(websocket: WebSocket):
    wss = WebSocketSession(websocket)
    await wss.accept_connection()
    await wss.listen_and_serve()