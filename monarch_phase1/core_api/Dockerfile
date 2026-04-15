FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY monarch_phase1/core_api/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monarch_phase1/core_api/app ./app
COPY monarch_phase1/core_api/alembic.ini ./alembic.ini
COPY monarch_phase1/core_api/migrations ./migrations
COPY monarch_phase1/core_api/start.sh ./start.sh

RUN chmod +x /app/start.sh

EXPOSE 8010

CMD ["/app/start.sh"]
