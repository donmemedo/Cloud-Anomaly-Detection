.PHONY: help install test run build deploy clean

help:
	@echo "Available commands:"
	@echo "  make install    Install dependencies"
	@echo "  make test       Run tests"
	@echo "  make run-dev    Run development server"
	@echo "  make build-dev  Build development Docker image"
	@echo "  make build-stg  Build staging Docker image"
	@echo "  make build-prod Build production Docker image"
	@echo "  make deploy-dev Deploy to development"
	@echo "  make clean      Clean up temporary files"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=main

run-dev:
	ENVIRONMENT=dev uvicorn main:app --host 0.0.0.0 --port 8001 --reload

run-stg:
	ENVIRONMENT=stg uvicorn main:app --host 0.0.0.0 --port 8002

run-prod:
	ENVIRONMENT=prod uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

build-dev:
	docker-compose -f docker-compose.dev.yml build

build-stg:
	docker-compose -f docker-compose.stg.yml build

build-prod:
	docker-compose -f docker-compose.prod.yml build

up-dev:
	docker-compose -f docker-compose.dev.yml up -d

up-stg:
	docker-compose -f docker-compose.stg.yml up -d

up-prod:
	docker-compose -f docker-compose.prod.yml up -d

deploy-dev: build-dev up-dev

deploy-stg: build-stg up-stg

deploy-prod: build-prod up-prod

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
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +