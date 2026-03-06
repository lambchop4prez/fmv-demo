#!/usr/bin/env -S just --justfile
# ^ A shebang isn't required, but allows a justfile to be executed
#   like a script, with `./.justfile test`, for example.

set quiet := true
set shell := ['bash', '-euo', 'pipefail', '-c']

registry := env("DOCKER_REGISTRY", "ghcr.io")
image_backend := env("DOCKER_IMAGE_BACKEND", "lambchop4prez/fmv-demo-backend")
image_frontend := env("DOCKER_IMAGE_FRONTEND", "lambchop4prez/fmv-demo-frontend")
version := env("NEW_VERSION", "0.0.0-dirty")
artifacts := justfile_dir() / "artifacts"
default_profile := "ci"

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
    typos

[group('check')]
[parallel]
analyze: spellcheck typecheck lint

[group('build')]
[group('docker')]
build-frontend-image: (_build-image './ui' image_frontend)

[group('build')]
[group('docker')]
build-backend-image: (_build-image '.' image_backend)

[group('build')]
[group('docker')]
_build-image context image:
    docker build {{ context }} -t {{ registry }}/{{ image }}:{{ version }}

[group('build')]
[parallel]
build: frontend::build build-frontend-image build-backend-image

[group('test')]
[parallel]
unit-test: frontend::unit-test backend::unit-test

[group('ci')]
ci:
    semantic-release -c .config/release.toml -v version --no-changelog --no-commit --no-tag

[group('ci')]
release:
    semantic-release -c .config/release.toml -v --strict version --skip-build --no-commit

[group('ci')]
publish: _publish-release _publish-images

[group('ci')]
_publish-release:
    semantic-release -c .config/release.toml publish

[group('ci')]
_tag-and-publish image:
    docker image tag {{ registry }}/{{ image }}:{{ version }} {{ registry }}/{{ image_backend }}:latest
    docker image push --all-tags {{ registry }}/{{ image }}

[group('ci')]
[parallel]
_publish-images: (_tag-and-publish image_frontend) (_tag-and-publish image_backend)

[doc("Brings up a specific profile. Can be 'ci', 'infra', 'backend', or 'frontend'")]
[group('ci')]
[group('dev')]
up profile=default_profile:
    docker compose --profile {{ profile }} up --detach --no-build

[doc("Brings down a specific profile. Can be 'ci', 'infra', 'backend', or 'frontend'")]
[group('ci')]
[group('dev')]
down profile=default_profile:
    docker compose --profile {{ profile }} down

_image-save filename registry image version:
    docker image save -o {{ artifacts }}/{{ filename }}-{{ version }}.tar.gz {{ registry }}/{{ image }}:{{ version }}

[doc('Collect artifacts for storage')]
[group('ci')]
[parallel]
artifacts: frontend::artifacts (_image-save "frontend" registry image_frontend version) (_image-save "backend" registry image_backend version)

[doc('Load docker image from artifact')]
[group('ci')]
[group('docker')]
_load-image image:
    docker image load --input {{ artifacts }}/{{ image }}-{{ version }}.tar.gz

[doc('Load container images from artifacts')]
[group('ci')]
[group('docker')]
[parallel]
load: (_load-image 'frontend') (_load-image 'backend')
    docker image ls --digests

[doc("Runs e2e tests and collects logs")]
[group('ci')]
e2e: frontend::e2e _e2e-logs

[doc('Collect logs from containers used in E2E testing')]
[group('ci')]
_e2e-logs:
    docker compose logs api > {{ justfile_dir() }}/ui/test/logs/api.log
    docker compose logs workers > {{ justfile_dir() }}/ui/test/logs/workers.log
    docker compose logs frontend > {{ justfile_dir() }}/ui/test/logs/frontend.log

[doc('Get image digest')]
_digest image:
    docker image inspect {{ registry }}/{{ image }}:{{ version }} | jq -r .[0].Descriptor.digest

[group('ci')]
[group('docker')]
digest-backend: (_digest image_backend)

[group('ci')]
[group('docker')]
digest-frontend: (_digest image_frontend)
