#!/usr/bin/env -S just --justfile
# ^ A shebang isn't required, but allows a justfile to be executed
#   like a script, with `./.justfile test`, for example.

set quiet
set shell := ['bash', '-euo', 'pipefail', '-c']

registry := env("DOCKER_REGISTRY", "ghcr.io")
image_backend := env("DOCKER_IMAGE_BACKEND", "lambchop4prez/fmv-demo-backend")
image_frontend := env("DOCKER_IMAGE_FRONTEND", "lambchop4prez/fmv-demo-frontend")
version := env("NEW_VERSION", "0.0.0-dirty")
artifacts := justfile_dir() / "artifacts"
default_profile := "ci"
cert_dir := justfile_dir() + '/.cert'

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

[doc("Initial setup of dev environment")]
[group('dev')]
setup:
    lefthook install
    mkcert --install
    mkdir -p {{ cert_dir }} && mkcert -key-file {{ cert_dir }}/key.pem -cert-file {{ cert_dir }}/cert.pem localhost 127.0.0.1 ::1

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
build: build-frontend-image build-backend-image

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
    docker image tag {{ registry }}/{{ image }}:{{ version }} {{ registry }}/{{ image }}:latest
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
    mkdir -p {{ artifacts }} && docker image save -o {{ artifacts }}/{{ filename }}-{{ version }}.tar.gz {{ registry }}/{{ image }}:{{ version }}

[doc('Collect artifacts for storage')]
[group('ci')]
[parallel]
artifacts: (_image-save "frontend" registry image_frontend version) (_image-save "backend" registry image_backend version)

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
    docker image inspect {{ registry }}/{{ image }}:{{ version }} | jq -r .[0].RepoDigests[0] | cut -d '@' -f 2

[group('ci')]
[group('docker')]
digest-backend: (_digest image_backend)

[group('ci')]
[group('docker')]
digest-frontend: (_digest image_frontend)

[doc("Rename the project from 'fmv-demo' to a new name across all tracked files. Prompts for missing values. Dry-run first.")]
[group('template')]
[script]
rename name="" owner="lambchop4prez" title="":
    #!/usr/bin/env bash
    set -euo pipefail

    old_owner="{{ owner }}"
    old_display="FastAPI MongoDB Vue Stack Demo"
    new_kebab="{{ name }}"
    new_title="{{ title }}"

    interactive=false
    if [[ -t 0 ]]; then interactive=true; fi

    if [[ -z "$new_kebab" && "$interactive" == true ]]; then
        new_kebab=$(gum input --placeholder "my-app" --prompt "New project name (kebab-case)? ")
    fi
    if [[ -z "$new_kebab" ]]; then
        just log error "usage: just rename <kebab-case-name> [owner] [title]"
        exit 1
    fi
    if [[ ! "$new_kebab" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]]; then
        just log error "project name must be kebab-case, got '$new_kebab'"
        exit 1
    fi
    if [[ "$new_kebab" == "fmv-demo" ]]; then
        just log warn "new name equals current name; nothing to do"
        exit 0
    fi

    new_owner="$old_owner"
    if [[ "$interactive" == true ]] && gum confirm "Replace GitHub owner '${old_owner}'?"; then
        new_owner=$(gum input --value "$old_owner" --prompt "New GitHub owner? ")
    fi

    if [[ "$new_owner" =~ [^a-zA-Z0-9._-] ]]; then
        just log error "owner must be alphanumeric (dots/dashes ok), got '$new_owner'"
        exit 1
    fi

    # Derive case variants from the kebab-case name (perl: portable macOS/Linux)
    new_pascal=$(perl -pe 's/(^|-)([a-z])/\u\2/g' <<< "$new_kebab")
    new_camel=$(perl -pe 's/-([a-z])/\u\1/g' <<< "$new_kebab")
    new_snake="${new_kebab//-/_}"
    new_screaming="${new_snake^^}"
    new_title="${new_title:-$(tr '-' ' ' <<< "$new_kebab" | perl -pe 's/\b([a-z])/\u\1/g')}"

    if [[ "${new_kebab}${new_owner}${new_title}" == *'|'* ]]; then
        just log error "name/owner/title must not contain '|'"
        exit 1
    fi

    # Ordered replacement pairs, most specific first
    pairs=(
        "${old_display}||${new_title}"
        "${old_owner}/fmv-demo||${new_owner}/${new_kebab}"
        "FMV Demo||${new_title}"
        "FMV Frontend||${new_title} Frontend"
        "FMV Backend||${new_title} Backend"
        "FMV||${new_pascal}"
        "fmv_demo||${new_snake}"
        "FMV_DEMO||${new_screaming}"
        "FmvDemo||${new_pascal}"
        "fmvDemo||${new_camel}"
        "fmv-demo||${new_kebab}"
    )
    if [[ "$new_owner" != "$old_owner" ]]; then
        pairs+=("${old_owner}||${new_owner}")
    fi

    scan_re=$(IFS='|'; echo "${pairs[*]%%||*}")

    just log info "dry run: 'fmv-demo' -> '${new_kebab}' (owner: '${new_owner}', title: '${new_title}')"
    total=0
    changed=()
    while IFS= read -r f; do
        n=$(grep -oE "$scan_re" "$f" 2>/dev/null | wc -l) || n=0
        if (( n > 0 )); then
            printf '  %-52s %s\n' "$f" "$n"
            changed+=("$f")
            total=$((total + n))
        fi
    done < <(git ls-files | grep -vE '(uv\.lock|pnpm-lock\.yaml|package-lock\.json)$')

    if (( total == 0 )); then
        just log warn "no matches found; nothing renamed"
        exit 0
    fi
    just log info "total: ${total} occurrences across ${#changed[@]} files"

    if [[ "$interactive" == true ]] && ! gum confirm "Apply rename to ${#changed[@]} files?"; then
        just log warn "aborted; no files changed"
        exit 0
    fi

    for f in "${changed[@]}"; do
        for pair in "${pairs[@]}"; do
            old="${pair%%||*}"
            new="${pair##*||}"
            perl -pi -e "s|\b\Q${old}\E\b|${new}|g" "$f"
        done
    done

    just log info "rename complete"
    just log info "manual follow-up:"
    just log info "  1. rename the checkout: mv ../$(basename "$PWD") ../${new_kebab}"
    just log info "  2. update the remote: git remote set-url origin git@github.com:${new_owner}/${new_kebab}.git"
    just log info "  3. review .secrets.env and .mise.toml (audience, docker image names)"
    just log info "  4. re-run: just setup && just analyze"
