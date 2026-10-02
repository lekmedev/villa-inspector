FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn[standard]

COPY server.py /app/server.py
COPY public /app/public

EXPOSE 80

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]
