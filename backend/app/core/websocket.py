from fastapi import WebSocket
from io import BytesIO
import pandas as pd
import os
import psutil
from time import time
import subprocess
import json
from time import sleep

from app.core.genai.gemini_wrapper import start_gemini_session
from app.core.database import db, storage
from app.core.logger import logger

ports = list(range(8501, 8599))

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
        self.dash_process = None
        os.makedirs(self.path, exist_ok=True)

        self.pid = None
 
    async def accept_connection(self) -> None:
        await self.websocket.accept()

    async def handle_disconnect(self) -> None:
        logger.info("Terminating session")
        self._stop_dashboard()
        self.__code.code = Code()
        await self._store_revision()
        ports.append(self.port)
        await self.websocket.close()

    async def listen_and_serve(self) -> None:
        try:
            while True:
                try:
                    ws_data = await self.websocket.receive()
                    if "text" in ws_data:
                        data = ws_data["text"]
                        if data.startswith('{'): 
                            self._process_signal(ws_data) 
                        else: 
                            resp = await self._process_chat(data)
                    elif "bytes" in ws_data:
                        data = ws_data["bytes"]
                        resp = await self._process_file(data)
                    elif "json" in ws_data:
                        self._process_signal(ws_data)
                    else:
                        resp = "Invalid message format"
        
                    if resp.startswith("```python"):
                        logger.info("got new code")
                        self.__code.extract(resp)
                        # await self.websocket.send_text(resp)
                        await self.__code.validate(self.__data.head(n=2))
                        logger.info("validated")
                        # on updates, clean up the dashboard before relaunching
                        self._stop_dashboard()
                        logger.info("Stopepd the old one")
                        # if self.dash_process:
                        #     self.dash_process.kill()
                        self.__curr_revision += 1
                        self._save_code()
                        self._launch_dashboard()
                        # await self.websocket.send_text(f'PORT:{self.port}')
                        await self.websocket.send_json(data={"PORT":self.port, "rev": self.__curr_revision})
                        # await self.websocket.send_text(self.__code.code) # replace with running deploy pipeline
                    else: 
                        await self.websocket.send_text(resp)
                except Exception as e:
                    await self.websocket.send_text(f"I don't know what went wrong. Ask me again!")
        except Exception as e:
            logger.exception(e)
        finally:
            logger.info("Disconnecting")
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

    async def _process_signal(self, ws_data):
        data = json.loads(ws_data)
        # check what they want, either switch revisions or something idk
        if "rev" in data:
            self._change_rev(data["rev"])

    def _launch_dashboard(self) -> None:
        base_path = self.path #self.path, "data.csv")
        dashboard_path = f"rev{self.__curr_revision}.py"  #os.path.join(self.path, f"rev{self.__curr_revision}.py")
        port = str(self.port)
        cmd = ['bash', RUNNER_PATH, base_path, dashboard_path, port]
        logger.info(f"starting {cmd}")
        self.dash_process = subprocess.Popen(cmd)
        logger.info(self.dash_process.pid)
        self.pid = self.dash_process.pid

    def _save_code(self) -> None:    
        out_path = os.path.join(self.path, f"rev{self.__curr_revision}.py")
        with open(out_path, "w") as file:
            file.write(self.__code.code)

    def _change_rev(self, rev: int) -> None:
        tmp = self.__curr_revision
        try:
            self._stop_dashboard()
            self.__curr_revision = rev
            self._launch_dashboard()
        except FileNotFoundError as e:
            logger.info(e)
            self.websocket.send_text("Revision not found!")
            self.__curr_revision = tmp
            self._launch_dashboard()
    
    def _stop_dashboard(self) -> None:
        if self.dash_process:
            ports.append(self.port)
            self.port = ports.pop(0)
            logger.info(f"stopping {self.dash_process.pid}")
            self._kill_process()


    def _kill_process(self) -> None:
        proc = psutil.Process(self.pid)
        logger.info(proc)
        proc.kill()
        code = proc.wait(timeout=5)
        logger.info(proc, code)

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

    async def validate(self, preview: pd.DataFrame) -> None:
        prev_error = self.__errors
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
                    code enclosed in ```python<code>``` For the data path, always use the env var CSV_PATH=os.getenv("CSV_PATH").
                    For reference heres a preview of their data {preview}. All columns in the dashboard must match these.
                    """
                )
                self.extract(resp.text)
                prev_error = self.__errors
                self._test()
    
    def _test(self) -> None:
        try:
            exec(self.code, self.__global_namespace)
            self.__errors = None
        except Exception as e:
            self.__errors = e

    def extract(self, text: str) -> None:
        code = text.removeprefix("```python").removesuffix("```")
        add_common_mistakes = """
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os
        """
        self.code = add_common_mistakes + code



