.PHONY: lint-backend
lint-backend:
	uv run ruff check
	uv run ruff format --check

.PHONY: lint-frontend
lint-frontend:
	pnpm run lint

.PHONY: lint
lint: lint-backend lint-frontend
