.PHONY: help build up down logs test lint install check-db clean

help:
	@echo "Available commands:"
	@echo "  make install       - Install Python dependencies"
	@echo "  make build         - Build Docker images"
	@echo "  make up            - Start Docker containers"
	@echo "  make down          - Stop Docker containers"
	@echo "  make logs          - View Docker logs"
	@echo "  make test          - Run pytest suite"
	@echo "  make lint          - Run code linting"
	@echo "  make check-db      - Test database connectivity"
	@echo "  make dev           - Start backend in development mode (local)"
	@echo "  make clean         - Remove containers and volumes"

install:
	cd backend && pip install -r requirements.txt

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f backend

test:
	cd backend && python -m pytest tests/ -v

lint:
	cd backend && python -m flake8 app/ --max-line-length=120 || true

check-db:
	cd backend && python scripts/check_db.py

dev:
	cd backend && uvicorn app.main:app --reload

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

.DEFAULT_GOAL := help
