set quiet := true
set shell := ['bash', '-euo', 'pipefail', '-c']

cert_dir := justfile_dir() + '/.cert'

[group('setup')]
uv-sync-dev:
    uv sync --locked --all-extras --dev

[group('check')]
lint: uv-sync-dev
    # just log info "Backend | Lint"
    uv run ruff check
    uv run ruff format --check

[group('check')]
typecheck: uv-sync-dev
    # just log info "Backend | Typecheck"
    uv run mypy .

[group('test')]
unit-test: uv-sync-dev
    # just log info "Backend | Running unit tests"
    uv run pytest

[doc("Start API in dev mode")]
[group('dev')]
api: uv-sync-dev
    uv run uvicorn api:app --ssl-keyfile={{ cert_dir }}/key.pem --ssl-certfile={{ cert_dir }}/cert.pem --port 8000 --reload 

[doc("Start celery worker in dev mode")]
[group('dev')]
workers: uv-sync-dev
    uv run celery -A workers worker -l INFO

[doc('Start both API and workers')]
[group('dev')]
[parallel]
dev: api workers
