FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY apps/monarch-core/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY apps/monarch-core/app ./app
COPY apps/monarch-core/alembic.ini ./alembic.ini
COPY apps/monarch-core/migrations ./migrations
COPY apps/monarch-core/start.sh ./start.sh

RUN chmod +x /app/start.sh

EXPOSE 8010

CMD ["/app/start.sh"]
