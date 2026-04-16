FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY canal_dark/ ./canal_dark/
ENV PYTHONPATH=/app
ENTRYPOINT ["python", "-m", "canal_dark"]
CMD ["--help"]
