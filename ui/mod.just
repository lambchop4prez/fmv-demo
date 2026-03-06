set quiet := true
set shell := ['bash', '-euo', 'pipefail', '-c']

version := env("NEW_VERSION", "0.0.0-dirty")
artifacts := justfile_dir() / "artifacts"
default_e2e_config := if env("CI", "false") == "true" { "ci" } else { 'dev' }

[group('setup')]
pnpm-install:
    pnpm install

[group('check')]
lint *args: pnpm-install
    # just log info "Frontend | Lint"
    pnpm run lint {{ args }}

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

[group('test')]
e2e config=default_e2e_config: pnpm-install
    pnpm run test:e2e:{{ config }}

[doc('Collect artifacts for storage')]
[group('ci')]
artifacts:
    mkdir -p {{ artifacts }} && tar czf {{ artifacts }}/dist-{{ version }}.tar.gz dist

[doc('Adds new component from Shadcn registry')]
[group('dev')]
add-component *args:
    pnpm dlx shadcn-vue@latest add {{ args }}

[doc('Generate API library')]
[group('dev')]
gen-client: pnpm-install
    pnpm run client:gen
