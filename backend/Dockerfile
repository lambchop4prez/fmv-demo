FROM --platform=$BUILDPLATFORM python:3.14-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:0.10.2 /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1

# Enable bytecode compilation, to improve cold-start performance.
ENV UV_COMPILE_BYTECODE=1

# Disable installer metadata, to create a deterministic layer.
ENV UV_NO_INSTALLER_METADATA=1

# Enable copy mode to support bind mount caching.
ENV UV_LINK_MODE=copy

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
COPY . /app

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# # Setup a non-root user
# RUN groupadd --system --gid 999 nonroot \
#   && useradd --system --gid 999 --uid 999 --create-home nonroot \
#   && chown -R nonroot:nonroot /app

# # Use the non-root user to run our application
# USER nonroot

CMD [ "uv", "run", "fastapi", "run", "--host", "0.0.0.0", "src/api" ]
