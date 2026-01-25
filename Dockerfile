FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY app ./app
COPY config ./config
COPY README.md ./README.md

CMD ["python", "-m", "app.run"]
