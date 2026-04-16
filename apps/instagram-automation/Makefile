.PHONY: install test lint clean queue approve docker-build

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

lint:
	python -m ruff check instagram_automation/
	python -m ruff format --check instagram_automation/

clean:
	rm -rf __pycache__/ */__pycache__/ */*/__pycache__/
	rm -rf queue.json output/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/

queue:
	python -m instagram_automation queue

approve:
	python -m instagram_automation approve 1

docker-build:
	docker build -t instagram-automation:latest .
