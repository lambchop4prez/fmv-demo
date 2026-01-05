#!/usr/bin/env -S just --justfile
# ^ A shebang isn't required, but allows a justfile to be executed
#   like a script, with `./.justfile test`, for example.
set quiet := true
set shell := ['bash', '-euo', 'pipefail', '-c']

[private]
default:
    just --list

[private]
log lvl msg *args:
    gum log --time rfc822 -s --level "{{ lvl }}" "{{ msg }}" {{ args }}

[group('setup')]
uv-sync-dev:
    uv sync --locked --all-extras --dev

[group('setup')]
pnpm-install:
    pnpm install

dev: uv-sync-dev
    uv run fastapi dev src/api

[group('check')]
lint-backend: uv-sync-dev
    uv run ruff check
    uv run ruff format --check

[group('check')]
lint-frontend: pnpm-install
    pnpm run lint

[group('check')]
[parallel]
lint: lint-frontend lint-backend

[group('check')]
typecheck-backend: uv-sync-dev
    uv run mypy .

[group('check')]
typecheck-frontend: pnpm-install
    pnpm run typecheck

[group('check')]
[parallel]
typecheck: typecheck-frontend typecheck-backend

[group('check')]
spellcheck:
    cspell .

[group('check')]
[parallel]
analyze: spellcheck typecheck lint

[group('build')]
build:
    docker compose build

[group('test')]
unit-test-frontend: pnpm-install
    pnpm run test:unit

[group('test')]
unit-test-backend: uv-sync-dev
    uv run pytest

[group('test')]
[parallel]
unit-test: unit-test-frontend unit-test-backend
