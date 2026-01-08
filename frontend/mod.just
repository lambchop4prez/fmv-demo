set quiet := true
set shell := ['bash', '-euo', 'pipefail', '-c']

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

[group('dev')]
dev: pnpm-install
    pnpm run dev
