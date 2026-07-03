FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

ENV TIKTOKEN_CACHE_DIR=/app/.tiktoken
RUN .venv/bin/python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"

COPY app ./app

FROM python:3.12-slim

RUN useradd --create-home app

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV TIKTOKEN_CACHE_DIR=/app/.tiktoken

USER app

EXPOSE 8083

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8083"]
