from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI

from app.api.router import router

app = FastAPI()

app.include_router(router=router)

@app.get("/health-check")
def health_check():
    return 'ok'