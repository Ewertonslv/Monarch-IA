.PHONY: install test lint clean run run-html run-pdf docker-build

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

lint:
	python -m ruff check pdf_factory/
	python -m ruff format --check pdf_factory/

clean:
	rm -rf output/
	rm -rf __pycache__/ */__pycache__/ */*/__pycache__/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/
	rm -rf build/ dist/

run:
	python -m pdf_factory run \
		--title "Guia de Reels" \
		--audience "criadores iniciantes" \
		--objective "publicar reels com consistencia" \
		--cta "Escolha seu nicho hoje e grave o primeiro reel."

run-html:
	python -m pdf_factory run \
		--title "Guia de Reels" \
		--audience "criadores iniciantes" \
		--objective "publicar reels com consistencia" \
		--format html

run-pdf:
	python -m pdf_factory run \
		--title "Guia de Reels" \
		--audience "criadores iniciantes" \
		--objective "publicar reels com consistencia" \
		--format pdf

docker-build:
	docker build -t pdf-factory:latest .

docker-run:
	docker run --rm -v $$(pwd)/output:/output pdf-factory:latest run \
		--title "Guia de Reels" \
		--audience "criadores iniciantes" \
		--objective "publicar reels com consistencia"
