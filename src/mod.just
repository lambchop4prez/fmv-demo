set quiet := true
set shell := ['bash', '-euo', 'pipefail', '-c']

tag := env("DOCKER_IMAGE_BACKEND", 'backend')
version := env("NEW_VERSION", "0.0.0-dirty")
artifacts := justfile_dir() / "artifacts"

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

[group('build')]
build:
    # just log info "Backend | Build"
    docker build . -t {{ tag }}:{{ version }}

[doc("Start API in dev mode")]
[group('dev')]
api: uv-sync-dev
    uv run fastapi dev api

[doc("Start celery worker in dev mode")]
[group('dev')]
workers: uv-sync-dev
    uv run celery -A workers worker -l INFO

[doc('Start both API and workers')]
[group('dev')]
[parallel]
dev: api workers

[doc('Collect artifacts for storage')]
[group('ci')]
artifacts:
    docker image save -o {{ artifacts }}/backend-{{ version }}.tar.gz {{ tag }}:{{ version }}

[doc('Load docker image from artifact')]
[group('ci')]
load:
    docker image load --input {{ artifacts }}/backend-{{ version }}.tar.gz
