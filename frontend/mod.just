set quiet := true
set shell := ['bash', '-euo', 'pipefail', '-c']

tag := env("DOCKER_IMAGE_FRONTEND", 'frontend')
version := env("NEW_VERSION", "0.0.0-dirty")
artifacts := justfile_dir() / "artifacts"

[group('setup')]
pnpm-install:
    pnpm install

[group('check')]
lint: pnpm-install
    # just log info "Frontend | Lint"
    pnpm run lint

[group('check')]
typecheck: pnpm-install
    # just log info "Frontend | Typecheck"
    pnpm run typecheck

[group('test')]
unit-test: pnpm-install
    # just log info "Frontend | Unit test"
    pnpm run test:unit

[group('build')]
build: pnpm-install
    # just log info "Frontend | Build"
    pnpm run build

[group('build')]
build-container:
    docker build . -t {{tag}}:{{version}}

[group('dev')]
dev: pnpm-install
    pnpm run dev

[group('test')]
e2e: pnpm-install
    pnpm run test:e2e

[group('ci')]
[doc('Collect artifacts for storage')]
artifacts:
    mkdir -p {{artifacts}} && tar czf {{artifacts}}/dist-{{version}}.tar.gz dist
    docker image save -o {{artifacts}}/frontend-{{version}}.tar.gz {{tag}}:{{version}}

[group('ci')]
[doc('Load docker image from artifact')]
load:
    docker image load --input {{artifacts}}/frontend-{{version}}.tar.gz
