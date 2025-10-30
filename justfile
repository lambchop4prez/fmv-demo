#!/usr/bin/env -S just --justfile
# ^ A shebang isn't required, but allows a justfile to be executed
#   like a script, with `./justfile test`, for example.

default:
    just --list
[group: 'setup']
uv-sync-dev:
    uv sync --locked --all-extras --dev

[group: 'setup']
pnpm-install:
    pnpm install

[group: 'check']
lint-backend: uv-sync-dev
    uv run ruff check
    uv run ruff format --check

[group: 'check']
lint-frontend: pnpm-install
    pnpm run lint

[group: 'lint', parallel]
lint: lint-frontend lint-backend

[group: 'check']
typecheck-backend: uv-sync-dev
    uv run mypy .

[group: 'check']
typecheck-frontend: pnpm-install
    pnpm run typecheck

[group: 'check', parallel]
typecheck: typecheck-frontend typecheck-frontend

[group: 'check']
spellcheck:
    cspell .

[group: 'check', parallel]
analyze: spellcheck typecheck lint

[group: 'build']
build:
    docker-compose build
