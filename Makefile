.PHONY: help install test run-dev run-stg run-prod build clean

help:
	@echo "Available commands:"
	@echo "  make help       Show this help"
	@echo "  make install    Install dependencies"
	@echo "  make test       Run tests"
	@echo "  make run-dev    Run development server locally"
	@echo "  make run-stg    Run staging server locally"
	@echo "  make run-prod   Run production server locally"
	@echo "  make build-dev  Build development Docker image"
	@echo "  make build-stg  Build staging Docker image"
	@echo "  make build-prod Build production Docker image"
	@echo "  make up-dev     Start development containers"
	@echo "  make up-stg     Start staging containers"
	@echo "  make up-prod    Start production containers"
	@echo "  make down-dev   Stop development containers"
	@echo "  make down-stg   Stop staging containers"
	@echo "  make down-prod  Stop production containers"
	@echo "  make logs-dev   Show development logs"
	@echo "  make logs-stg   Show staging logs"
	@echo "  make logs-prod  Show production logs"
	@echo "  make clean      Clean up temporary files"

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

run-dev:
	ENVIRONMENT=dev python src/main.py

run-stg:
	ENVIRONMENT=stg python src/main.py

run-prod:
	ENVIRONMENT=prod python src/main.py

build-dev:
	docker build --target development -t cloud-anomaly-dev .

build-stg:
	docker build --target production -t cloud-anomaly-stg .

build-prod:
	docker build --target production -t cloud-anomaly-prod .

up-dev:
	docker-compose -f docker-compose.dev.yml up -d

up-stg:
	docker-compose -f docker-compose.stg.yml up -d

up-prod:
	docker-compose -f docker-compose.prod.yml up -d

down-dev:
	docker-compose -f docker-compose.dev.yml down

down-stg:
	docker-compose -f docker-compose.stg.yml down

down-prod:
	docker-compose -f docker-compose.prod.yml down

logs-dev:
	docker-compose -f docker-compose.dev.yml logs -f

logs-stg:
	docker-compose -f docker-compose.stg.yml logs -f

logs-prod:
	docker-compose -f docker-compose.prod.yml logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +