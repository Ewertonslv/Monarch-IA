FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY tiktok_shop/ ./tiktok_shop/
ENV PYTHONPATH=/app
ENTRYPOINT ["python", "-m", "tiktok_shop"]
CMD ["--help"]
