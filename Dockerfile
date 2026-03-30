# Inspired from https://github.com/astral-sh/uv-docker-example/blob/dee88a8c43be3b16b0ad58f0daee5eaee7e2157a/multistage.Dockerfile.

# Keep uv version in sync with pyproject.toml's `tool.uv.required-version`.
# Keep Python version in sync with:
# - pyproject.toml's `project.requires-python`.
# - the main stage below.
FROM ghcr.io/astral-sh/uv:0.11.2-python3.12-trixie-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /venv

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project
RUN --mount=type=bind,source=skeleton,target=skeleton_tmp \
    mkdir app && \
    uv run python -m skeleton_tmp && \
    mv app/skeleton skeleton && \
    rm -r app

# Keep this synced with the `builder` stage above.
FROM python:3.12-slim-trixie

COPY --from=builder /venv app

ENV PATH="/app/.venv/bin:$PATH"

COPY app app

ENV ATOTI_HIDE_EULA_MESSAGE=true
ENV PORT=80

EXPOSE $PORT

CMD ["python", "-O", "-u", "-m", "app"]
