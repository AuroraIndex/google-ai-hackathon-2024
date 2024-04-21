from fastapi import WebSocket, WebSocketDisconnect, WebSocketException
from app.core.genai.gemini_wrapper import start_gemini_session
# store messages and a reference to the current and all past iterations
# on close/save -> save whole state to db. when user tries to load past session, pull the whole state from db
class WebSocketSession:
    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket
        self.gemini = start_gemini_session()

    async def accept_connection(self) -> None:
        await self.websocket.accept()

    async def listen_and_serve(self) -> None:
        try:
            while True:
                data = await self.websocket.receive_text()
                resp = await self.process_message(data)
                await self.websocket.send_text(resp)
        except Exception as e:
            print(e)
        finally:
            await self.handle_disconnect()
    
    async def handle_disconnect(self) -> None:
        await self.websocket.close()

    async def process_message(self, message: str) -> str:
        response = await self.gemini.send_message_async(message)
        resp = response.text
        return resp