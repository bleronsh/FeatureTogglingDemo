FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY app ./app
COPY README.md ./README.md

CMD ["python", "-m", "app.run"]
