.PHONY: install test lint clean run add catalog shortlist docker-build

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

lint:
	python -m ruff check achadinhos/
	python -m ruff format --check achadinhos/

clean:
	rm -rf __pycache__/ */__pycache__/ */*/__pycache__/
	rm -rf catalog.json output/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/

add:
	python -m achadinhos add \
		--title "Escova Secadora Premium" \
		--category "beleza" \
		--source "fornecedor-test" \
		--price 70 \
		--sale-price 179 \
		--visual-hook 9 \
		--novelty 7 \
		--demo 8

catalog:
	python -m achadinhos catalog

shortlist:
	python -m achadinhos shortlist --limit 5

docker-build:
	docker build -t achadinhos:latest .
