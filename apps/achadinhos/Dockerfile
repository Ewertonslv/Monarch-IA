FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY achadinhos/ ./achadinhos/

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "-m", "achadinhos"]
CMD ["--help"]
