FROM python:3.13-slim AS deps
# uv ships as a static binary; bring it into the image from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# keep the venv outside the project dir so runtime bind-mounts can never shadow it
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked

FROM deps AS dev
# no app code baked in: compose bind-mounts ./backend over /app at runtime
