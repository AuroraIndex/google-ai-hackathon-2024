FROM python:3.12-slim-bullseye

WORKDIR /app

COPY ./backend/requirements.txt .

RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./backend .

EXPOSE 8000 
EXPOSE 8501-8599

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-max-size 110000000"]