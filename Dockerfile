FROM python:3.12-slim AS build

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install system-level dependencies. Don't let poetry handle the venv
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc libpython3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install poetry

# Copy source code. NOTE: Build should NOT contain tests, we skip them on purpose, they should run only on CI
WORKDIR /app
COPY poetry.lock pyproject.toml ./
COPY app app
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# Start distroless
FROM al3xos/python-distroless:3.12-debian12 AS deploy
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
COPY --from=build --chown=65532:65532 ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=build --chown=65532:65532 /app /app

ENV PYTHONPATH=/app/app
ENV PATH="${PATH}:${VIRTUAL_ENV}/bin"
EXPOSE 9000

ENTRYPOINT ["/app/.venv/bin/uvicorn", "main:app", \
    "--host", "0.0.0.0", \
    "--port", "9000", \
    "--lifespan", "on", \
    "--no-proxy-headers"]