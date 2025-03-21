FROM python:3.13-slim

WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin" \
    PYTHONPATH=. \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY src/main.py ./
COPY requirements.txt ./

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install curl -y && \
    python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["python", "main.py"]
