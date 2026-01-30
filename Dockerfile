FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir pyyaml

COPY app ./app
COPY config ./config
COPY README.md ./README.md
test change bla bla bla
CMD ["python", "-m", "app.run"]
