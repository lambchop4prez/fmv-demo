#!/usr/bin/env -S just --justfile
# ^ A shebang isn't required, but allows a justfile to be executed
#   like a script, with `./.justfile test`, for example.

set quiet := true
set shell := ['bash', '-euo', 'pipefail', '-c']

mod frontend 'frontend/'
mod backend 'backend/'

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
    # just log info "Spellcheck"
    cspell .

[group('check')]
[parallel]
analyze: spellcheck typecheck lint

[group('build')]
[parallel]
build: frontend::build backend::build

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

[doc('Bring up only backing infrastructure (Mongo and RabbitMQ)')]
[group('dev')]
infra-up:
    docker compose --profile infra up -d

[doc('Bring down backing infrastructure')]
[group('dev')]
infra-down:
    docker compose --profile infra down

[doc('Bring up backend')]
[group('dev')]
backend-up:
    docker compose --profile backend up -d

[doc('Tear down backend')]
[group('dev')]
backend-down:
    docker compose --profile backend down
