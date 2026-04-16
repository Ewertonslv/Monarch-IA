FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY solo_leveling_lab/ ./solo_leveling_lab/
ENV PYTHONPATH=/app
ENTRYPOINT ["python", "-m", "solo_leveling_lab"]
CMD ["--help"]
