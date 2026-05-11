# Development Guide

## Initial setup

After cloning the repo, the environment needs to be setup.

First install all the required tools

```bash
mise install
```

Then, setup git hooks and TLS certificates

```bash
just setup
```

## Development

This project uses docker compose to define all services needed to run it. The `just up` command 
exposes the different variations of environment to bring up.

```sh
just up infra    # Only bring up backing infrastructure
just up backend  # Bring up infrastructure, api, and workers. Useful for frontend development.
just up frontend # Bring up infrastructure and frontend. Useful for backend development
```

With the required infrastructure up, development servers can be started with the following commands.

```sh
just frontend dev
just backend dev
```

## Code quality

Code quality is managed in CI via the `just analyze` command, which can be used during to development
to ensure the build will pass. Additionally, `lefthook` is installed to run a number of static
analysis scripts on pre-commit. These can be run with the following command:

```sh
lefthook run pre-commit  # will only run on staged changes
```

## API Versioning and Breaking Changes

The API is versioned with an `/api/v{n}/` endpoint prefix that maps to routers defined in 
`src/api/v{n}/router.py`. Within a defined version only additive changes can be made, no
modifications or deletions. To make a breaking change, a new router should be defined and
mounted to the main API app in `src/api/main.py`.

## Commit Message

Use [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/) messages for commits. 
These determine whether a new version needs to be released.

Format: `<type>(optional scope): <description>`

Add a bang `!` character before the colon `:` to denote a breaking change. This will increment the
major version.

### Types:

 - `feat` - New features, increments minor version.
 - `fix` - Fixes a defect, increments patch version.
 - `test` - Adds/updates automated tests.
 - `build` - Changes regarding the build process.
 - `ci` - Changes to the CI pipeline.
 - `docs` - Documentation changes.
 - `style` - Code style changes.
 - `refactor` - Code refactoring.
 - `perf` - Performance enhancement
 - `chore` - Anything else that doesn't fit above.

### Scopes:

Common scopes include (others can be used):

 - `ui` - Frontend changes
 - `api` - API Changes
 - `workers` - Celery workers
 - `deps` - Software dependencies (mostly used by Renovate)

### Examples:

```
feat(api)!: New Robot V2 API.
fix(ui): Robot button shows error on HTTP 500.
chore(deps): Remove unused dependency `some-package`.
```
