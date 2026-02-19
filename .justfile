#!/usr/bin/env -S just --justfile
# ^ A shebang isn't required, but allows a justfile to be executed
#   like a script, with `./.justfile test`, for example.

set quiet := true
set shell := ['bash', '-euo', 'pipefail', '-c']

tag := env("DOCKER_IMAGE_BACKEND", 'backend')
version := env("NEW_VERSION", "0.0.0-dirty")
artifacts := justfile_dir() / "artifacts"

mod frontend 'ui/'
mod backend 'src/'

[private]
default:
    just log info "Frontend"
    just --list frontend
    just log info "Backend"
    just --list backend
    just log info "All"
    just --list

[private]
log lvl msg *args:
    gum log --time rfc822 -s --level "{{ lvl }}" "{{ msg }}" {{ args }}

[group('check')]
[parallel]
lint: frontend::lint backend::lint

[group('check')]
[parallel]
typecheck: frontend::typecheck backend::typecheck

[group('check')]
spellcheck:
    cspell .

[group('check')]
[parallel]
analyze: spellcheck typecheck lint

[group('build')]
build-api:
    # just log info "Backend | Build"
    docker build . -t {{ tag }}:{{ version }}
[group('build')]
[parallel]
build: frontend::build frontend::build-container build-api

[group('test')]
[parallel]
unit-test: frontend::unit-test backend::unit-test

[group('ci')]
ci:
    semantic-release -c .config/release.toml -v version --no-changelog --no-commit --no-tag

[group('ci')]
release:
    semantic-release -c .config/release.toml -v --strict version --skip-build

[group('ci')]
publish:
    semantic-release -c .config/release.toml publish

[group('ci')]
up:
    docker compose --profile ci up --detach --no-build

[group('ci')]
down:
    docker compose --profile ci down

[doc('Collect artifacts for storage')]
[group('ci')]
[parallel]
artifacts: frontend::artifacts backend::artifacts

[doc('Load container images from artifacts')]
[group('ci')]
[parallel]
load: frontend::load backend::load

[doc('Bring up only backing infrastructure (Mongo and RabbitMQ)')]
[group('dev')]
infra-up:
    docker compose --profile infra up --detach

[doc('Bring down backing infrastructure')]
[group('dev')]
infra-down:
    docker compose --profile infra down

[doc('Bring up backend')]
[group('dev')]
backend-up:
    docker compose --profile backend up --detach

[doc('Tear down backend')]
[group('dev')]
backend-down:
    docker compose --profile backend down
