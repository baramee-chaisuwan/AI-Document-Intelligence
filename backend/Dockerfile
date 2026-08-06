FROM python:3.13.11-slim-bookworm@sha256:20080e807bfc404f8450b185cf0fc95d553462673598549613735f70a5b4d5d0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    ENVIRONMENT=production \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

RUN groupadd --gid 10001 app \
    && useradd \
        --uid 10001 \
        --gid app \
        --create-home \
        --home-dir /home/app \
        --shell /usr/sbin/nologin \
        app

COPY requirements.txt ./requirements.txt

RUN python -m pip install \
        --no-cache-dir \
        --no-compile \
        torch==2.13.0 \
        --index-url https://download.pytorch.org/whl/cpu \
    && python -m pip install \
        --no-cache-dir \
        --no-compile \
        --requirement requirements.txt

COPY app ./app
COPY alembic ./alembic
COPY scripts ./scripts
COPY alembic.ini main.py ./

RUN mkdir -p \
        /app/.cache/huggingface \
    && chown -R app:app \
        /app/.cache

USER 10001:10001

EXPOSE 8080

HEALTHCHECK \
    --interval=30s \
    --timeout=5s \
    --start-period=30s \
    --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.getenv('PORT', '8080')}/health/\", timeout=3).read()"]

CMD ["python", "scripts/run_api.py"]
