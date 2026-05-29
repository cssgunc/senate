FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    UPLOAD_DIR=/app/uploads

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.prod.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.prod.txt

COPY app ./app
COPY script ./script

RUN mkdir -p /app/uploads \
    && chgrp -R 0 /app \
    && chmod -R g=u /app

EXPOSE 8000

CMD ["sh", "-c", "python -m script.init_db && uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers"]
