# =============================================================================
# IPAM PoC - Makefile
# Common commands for development and deployment
# =============================================================================

.PHONY: help build up down logs dev prod test lint clean

# Default target
help:
	@echo "IPAM PoC - Available Commands"
	@echo "=============================="
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment (hot-reload)"
	@echo "  make dev-logs     - View development logs"
	@echo "  make dev-down     - Stop development environment"
	@echo ""
	@echo "Production:"
	@echo "  make build        - Build production images"
	@echo "  make up           - Start production environment"
	@echo "  make down         - Stop production environment"
	@echo "  make logs         - View production logs"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run backend tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run linters"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Remove containers, images, and volumes"
	@echo "  make shell-back   - Open shell in backend container"
	@echo "  make shell-front  - Open shell in frontend container"
	@echo ""
	@echo "NetBox:"
	@echo "  make netbox-up    - Start NetBox (dev)"
	@echo "  make netbox-down  - Stop NetBox"
	@echo "  make netbox-logs  - View NetBox logs"
	@echo "  make stack-up     - Start full stack (IPAM + NetBox)"
	@echo ""

# =============================================================================
# Development
# =============================================================================

dev:
	docker compose -f docker-compose.dev.yml up --build

dev-detach:
	docker compose -f docker-compose.dev.yml up --build -d

dev-logs:
	docker compose -f docker-compose.dev.yml logs -f

dev-down:
	docker compose -f docker-compose.dev.yml down

dev-rebuild:
	docker compose -f docker-compose.dev.yml down
	docker compose -f docker-compose.dev.yml build --no-cache
	docker compose -f docker-compose.dev.yml up

# =============================================================================
# Production
# =============================================================================

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

status:
	docker compose ps

# =============================================================================
# Testing
# =============================================================================

test:
	cd backend && uv run pytest -v

test-cov:
	cd backend && uv run pytest --cov=app --cov-report=html --cov-report=term

test-docker:
	docker compose exec backend pytest -v

# =============================================================================
# Linting
# =============================================================================

lint:
	cd backend && uv run ruff check .
	cd frontend && npm run lint

lint-fix:
	cd backend && uv run ruff check --fix .
	cd frontend && npm run lint -- --fix

format:
	cd backend && uv run ruff format .
	cd frontend && npm run format

# =============================================================================
# Utilities
# =============================================================================

shell-back:
	docker compose exec backend /bin/bash

shell-front:
	docker compose exec frontend /bin/sh

clean:
	docker compose down -v --rmi local
	docker compose -f docker-compose.dev.yml down -v --rmi local
	docker system prune -f

# =============================================================================
# Local Development (without Docker)
# =============================================================================

install-backend:
	cd backend && uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"

install-frontend:
	cd frontend && npm install

run-backend:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8001

run-frontend:
	cd frontend && npm run dev

# =============================================================================
# NetBox (Development)
# =============================================================================

netbox-up:
	docker compose -f docker-compose.netbox.yml up -d
	@echo "NetBox starting... wait ~2 minutes for initialization"
	@echo "Access: http://localhost:8000"
	@echo "Login: admin / admin"
	@echo "API Token: 0123456789abcdef0123456789abcdef01234567"

netbox-down:
	docker compose -f docker-compose.netbox.yml down

netbox-logs:
	docker compose -f docker-compose.netbox.yml logs -f

netbox-status:
	docker compose -f docker-compose.netbox.yml ps

netbox-clean:
	docker compose -f docker-compose.netbox.yml down -v

# Full stack (IPAM + NetBox)
stack-up:
	docker compose -f docker-compose.netbox.yml up -d
	@echo "Waiting for NetBox to be healthy..."
	@sleep 120
	NETBOX_URL=http://host.docker.internal:8000 NETBOX_TOKEN=0123456789abcdef0123456789abcdef01234567 docker compose up -d

stack-down:
	docker compose down
	docker compose -f docker-compose.netbox.yml down

stack-logs:
	docker compose logs -f & docker compose -f docker-compose.netbox.yml logs -f

# =============================================================================
# Database / Migrations (future)
# =============================================================================

# migrate:
# 	docker compose exec backend alembic upgrade head

# migrate-create:
# 	docker compose exec backend alembic revision --autogenerate -m "$(name)"
