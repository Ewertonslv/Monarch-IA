FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Legado: use o Dockerfile canônico em apps/whatsapp-notion-bot/Dockerfile.

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY whatsapp_notion_bot/requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY whatsapp_notion_bot ./whatsapp_notion_bot

EXPOSE 8001

CMD ["uvicorn", "whatsapp_notion_bot.main:app", "--host", "0.0.0.0", "--port", "8001"]
