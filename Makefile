.PHONY: lint-backend
lint-backend:
	uv run ruff check
	uv run ruff format --check

.PHONY: lint-frontend
lint-frontend:
	pnpm run lint

.PHONY: lint
lint: lint-backend lint-frontend

.PHONY: typecheck-backend
typecheck-backend:
	uv run mypy .

.PHONY: typecheck-frontend
typecheck-frontend:
	pnpm run typecheck

.PHONY: typecheck
typecheck: typecheck-backend typecheck-frontend

.PHONY: analyze
analyze: lint typecheck

.PHONY: build
build:
	docker compose build
