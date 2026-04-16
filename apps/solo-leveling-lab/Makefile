.PHONY: install test lint clean docker-build
install: pip install -r requirements.txt
test: python -m pytest tests/ -v
lint: python -m ruff check solo_leveling_lab/
clean: rm -rf __pycache__/ */__pycache__/ output/ .pytest_cache/ *.egg-info/
docker-build: docker build -t solo-leveling-lab:latest .
