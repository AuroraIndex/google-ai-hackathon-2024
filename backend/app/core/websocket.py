from fastapi import WebSocket
from io import BytesIO
import pandas as pd
import os
from time import time
import subprocess
import sys

from app.core.genai.gemini_wrapper import start_gemini_session
from app.core.database import db, storage
from app.core.logger import logger

ports = ["8501", "8502", "8503", "8504", "8505"]

BASE_DATA_PATH="./_server_data"
RUNNER_PATH="./launch_streamlit.sh"
# store messages and a reference to the current and all past iterations
# on close/save -> save whole state to db. when user tries to load past session, pull the whole state from db
class WebSocketSession:

    global ports

    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket
        self.created = int(time())
        self.gemini = start_gemini_session()
        self.__db = db
        self.__blob = storage
        self.__revision_ids = []
        self.__curr_revision = 0
        self.__data: pd.DataFrame = None
        self.__code = Code()
        self.path = BASE_DATA_PATH + f"/{self.created}"
        self.port = ports.pop(0)
        self.process = None
        os.makedirs(self.path, exist_ok=True)


    async def accept_connection(self) -> None:
        await self.websocket.accept()

    async def handle_disconnect(self) -> None:
        self.process.terminate()
        await self._store_revision()
        ports.append(self.port)
        await self.websocket.close()

    async def listen_and_serve(self) -> None:
        try:
            while True:
                ws_data = await self.websocket.receive()
                if "text" in ws_data:
                    data = ws_data["text"]
                    resp = await self._process_chat(data)
                elif "bytes" in ws_data:
                    data = ws_data["bytes"]
                    resp = await self._process_file(data)

                if resp.startswith("```python"):
                    self.__code._extract(resp)
                    await self.websocket.send_text(resp)
                    await self.__code._validate(self.__data.head(n=2))
                    self.__curr_revision += 1
                    self._save_code()
                    self._launch_dashboard()        
                    await self.websocket.send_text(self.__code.code) # replace with running deploy pipeline
                await self.websocket.send_text(resp)
        except Exception as e:
            logger.exception(e)
        finally:
            await self.handle_disconnect()

    async def _process_chat(self, message: str) -> str:
        response = await self.gemini.send_message_async(message)
        resp = response.text
        return resp

    async def _process_file(self, file: bytes) -> str:
        try:
            self.__data = pd.read_csv(BytesIO(file), on_bad_lines='skip')
            full_path = os.path.join(self.path, "data.csv")
            os.environ["CSV_PATH"] = full_path

            self.__data.to_csv(full_path)
            preview = self.__data.head(n=5)

            response = await self.gemini.send_message_async(
                f"""
                Here is a preview of the data they provided: {preview}. Do not mkae up new columns, only use what is in the data already.
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


    def _launch_dashboard(self) -> None:
        data_path = os.path.join(self.path, "data.csv")
        dashboard_path = os.path.join(self.path, f"rev{self.__curr_revision}.py")
        port = self.port
        self.process = subprocess.Popen(['bash', RUNNER_PATH, data_path, dashboard_path, port])

    def _save_code(self) -> None:    
        out_path = os.path.join(self.path, f"rev{self.__curr_revision}.py")
        with open(out_path, "w") as file:
            file.write(self.__code.code)


class Code:
    def __init__(self) -> None:
        self.code: str | None = None
        self.gemini_lite = start_gemini_session(lite=True)
        self.__errors: str | None = "untested"
        self.__global_namespace = {
            '__builtins': __builtins__,
            'pandas': __import__('pandas'),
            'streamlit': __import__('streamlit'),
            'plotly': __import__('plotly'),
            'matplotlib': __import__('matplotlib'),
            'seaborn': __import__('seaborn')
        }

    async def _validate(self, preview: pd.DataFrame) -> None:
        self._test()
        while self.__errors:
            logger.warning(self.__errors)
            if self.__errors:
                resp = await self.gemini_lite.send_message_async(
                    f"""
                    This code:
                    ```
                    {self.code}
                    ```
                    produced this error during execution: {self.__errors}.
                    Fix the code. Do not include anything else. No context or explanations. Only the corrected 
                    code enclosed in ```python<code>``` For the data path, always use the env var CSV_PATH=os.getenv("CSV_PATH).
                    For reference heres a preview of their data {preview}. All columns in the dashboard must match these.
                    """
                )
                self._extract(resp.text)
                self._test()
    
    def _test(self) -> None:
        try:
            exec(self.code, self.__global_namespace)
            self.__errors = None
        except Exception as e:
            self.__errors = e

    def _extract(self, text: str) -> None:
        self.code = text.removeprefix("```python").removesuffix("```")