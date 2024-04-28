source .venv/Scripts/activate

uvicorn app.main:app --reload --ws-max-size 110000000
