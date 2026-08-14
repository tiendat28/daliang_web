FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-vie poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
COPY celery_app.py tasks.py ./
COPY extract ./extract
COPY ocr ./ocr
COPY preview ./preview

RUN pip install --no-cache-dir .

CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]
