# Development commands for Whiteboard App

.PHONY: help setup up down build clean logs test lint format

# Default target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial setup - copy .env and build containers
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please update .env with your settings"; \
	else \
		echo ".env already exists"; \
	fi
	@make build

build: ## Build all containers
	docker-compose build

up: ## Start all services
	docker-compose up -d

up-logs: ## Start all services with logs
	docker-compose up

down: ## Stop all services
	docker-compose down

clean: ## Stop services and remove volumes
	docker-compose down -v
	docker system prune -f

logs: ## Show logs for all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

logs-db: ## Show database logs
	docker-compose logs -f db

test: ## Run tests
	docker-compose exec backend pytest

test-frontend: ## Run frontend tests
	docker-compose exec frontend npm test

lint: ## Run linting
	docker-compose exec backend flake8 .
	docker-compose exec backend black --check .
	docker-compose exec frontend npm run lint

format: ## Format code
	docker-compose exec backend black .
	docker-compose exec frontend npm run format

shell-backend: ## Open shell in backend container
	docker-compose exec backend bash

shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec db psql -U postgres -d whiteboard_dev

migrate: ## Run database migrations
	docker-compose exec backend alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create name=migration_name)
	docker-compose exec backend alembic revision --autogenerate -m "$(name)"

reset-db: ## Reset database (WARNING: This will delete all data)
	docker-compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS whiteboard_dev;"
	docker-compose exec db psql -U postgres -c "CREATE DATABASE whiteboard_dev;"
	@make migrate

# Work Log Management
log-new: ## Create new daily work log (usage: make log-new TASK=task_name)
	@if [ -z "$(TASK)" ]; then \
		echo "Usage: make log-new TASK=task_name"; \
		echo "Example: make log-new TASK=backend-api"; \
	else \
		cp docs/logs/template_daily.md docs/logs/$$(date +%Y-%m-%d)_$(TASK).md; \
		echo "Created work log: docs/logs/$$(date +%Y-%m-%d)_$(TASK).md"; \
	fi

log-weekly: ## Create weekly summary
	@cp docs/logs/template_weekly.md docs/logs/$$(date +%Y-%m)_week$$(( ($$(date +%U) % 4) + 1 ))_summary.md
	@echo "Created weekly summary: docs/logs/$$(date +%Y-%m)_week$$(( ($$(date +%U) % 4) + 1 ))_summary.md"

log-list: ## List recent work logs
	@echo "Recent work logs:"
	@ls -t docs/logs/*.md | grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}" | head -10