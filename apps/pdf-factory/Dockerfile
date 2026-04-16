FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pdf_factory/ ./pdf_factory/
COPY templates/ ./templates/

ENV PYTHONPATH=/app
ENV PDF_FACTORY_OUTPUT_DIR=/output

ENTRYPOINT ["python", "-m", "pdf_factory"]
CMD ["--help"]
