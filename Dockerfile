FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml setup.cfg ./
COPY agents ./agents
COPY core ./core
COPY interfaces ./interfaces
COPY storage ./storage
COPY tools ./tools
COPY config.py ./
COPY main.py ./

RUN pip install --upgrade pip setuptools wheel \
    && pip install .

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["python", "main.py"]
