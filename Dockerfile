FROM python:3.12-slim-bookworm AS backend-builder

EXPOSE 8080

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY uv.lock uv.lock
COPY pyproject.toml pyproject.toml
RUN uv sync --frozen
COPY . /app

# ENTRYPOINT ["python", "main.py"]
# FastAPI アプリケーション (backend/main.py 内の app) を起動
ENTRYPOINT [".venv/bin/python", "main.py"]