.PHONY: build up down logs test

# Load .env file
-include .env
export

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

# Production commands
build-prod:
	docker-compose -f docker-compose.prod.yml build

up-prod:
	docker-compose -f docker-compose.prod.yml up -d

down-prod:
	docker-compose -f docker-compose.prod.yml down

# Database migrations (Alembic)
migrate:
	docker-compose exec app alembic upgrade head

makemigrations:
	docker-compose exec app alembic revision --autogenerate -m "$(m)"
