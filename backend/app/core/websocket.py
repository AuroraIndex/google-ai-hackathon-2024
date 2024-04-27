from fastapi import WebSocket, WebSocketDisconnect, WebSocketException
from io import BytesIO
import pandas as pd
from time import time

from app.core.genai.gemini_wrapper import start_gemini_session
from app.core.database import db, storage
from app.core.logger import logger


# store messages and a reference to the current and all past iterations
# on close/save -> save whole state to db. when user tries to load past session, pull the whole state from db
class WebSocketSession:
    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket
        self.created = int(time())
        self.gemini = start_gemini_session()
        self.gemini_lite = start_gemini_session(lite=True)
        self.__db = db
        self.__blob = storage
        self.__revision_ids = []
        self.__curr_revision = {}
        self.__data = None
        self.__code = None

    async def accept_connection(self) -> None:
        await self.websocket.accept()

    async def handle_disconnect(self) -> None:
        await self._store_revision()
        await self.websocket.close()

    async def listen_and_serve(self) -> None:
        try:
            while True:
                ws_data = await self.websocket.receive()
                logger.info("Received message")
                if "text" in ws_data:
                    data = ws_data["text"]
                    resp = await self._process_chat(data)
                elif "bytes" in ws_data:
                    data = ws_data["bytes"]
                    resp = await self._process_file(data)

                logger.info(resp)
                if resp.startswith("```python"):
                    self.__code = self._extract_code(resp)
                    await self._validate_code()                        
                    await self.websocket.send_text(self.__code) # replace with running deploy pipeline
                await self.websocket.send_text(resp)
        except Exception as e:
            logger.exception(e)
        finally:
            await self.handle_disconnect()

    async def _validate_code(self) -> None:
        errors = "untested"
        while errors:
            errors = self._test_code()
            logger.warning(errors)
            if errors:
                resp = await self.gemini_lite.send_message_async(
                    f"""
                    This code:
                    ```
                    {self.__code}
                    ```
                    produced this error during execution: {errors}.
                    Fix the code. Do not include anything else. No context or explanations. Only code enclosed in ```python<code>```
                    """
                )
                self.__code = self._extract_code(resp.text)
    
    def _test_code(self) -> str | None:
        try:
            exec(self.__code)
            return None
        except Exception as e:
            return str(e)

    def _extract_code(self, text: str) -> str:
        return text.removeprefix("```python").removesuffix("```")

    async def _process_chat(self, message: str) -> str:
        response = await self.gemini.send_message_async(message)
        resp = response.text
        return resp

    async def _process_file(self, file: bytes) -> str:
        try:
            self.__data = pd.read_csv(BytesIO(file), on_bad_lines='skip')
            preview = self.__data.head(n=10)
            response = await self.gemini.send_message_async(
                f"""
                Here is a preview of the data they provided: {preview}.
                """
            )
            return response.text
        except pd.errors.ParserError as e:
            logger.exception(e)
            resp = "Error parsing file. Only `.csv` are currently supported"
        except Exception as e:
            logger.exception(e)
            resp = f"Something went wrong: {e}"
        return resp


    

    async def _store_revision(self) -> None:
        # upload to blob
        # store ref in db
        # append id to self.revisions
        pass

    async def _load_revision(self):
        pass