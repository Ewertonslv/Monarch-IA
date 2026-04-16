.PHONY: install test lint clean docker-build
install: pip install -r requirements.txt
test: python -m pytest tests/ -v
lint: python -m ruff check canal_dark/
clean: rm -rf __pycache__/ */__pycache__/ output/ .pytest_cache/ *.egg-info/
docker-build: docker build -t canal-dark:latest .
