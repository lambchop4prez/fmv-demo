
lint *args:
    cargo clippy {{ args }}

format:
    cargo fmt

analyze: format lint
