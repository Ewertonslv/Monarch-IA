FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY instagram_automation/ ./instagram_automation/

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "-m", "instagram_automation"]
CMD ["--help"]
