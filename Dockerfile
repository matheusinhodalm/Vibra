# ---- VIBRA (Flask) - Dockerfile ----
FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY vibra_site/ /app/
COPY requirements.txt /app/requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PORT=8080     FLASK_ENV=production     DATABASE=/app/data/vibra.db

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8080
RUN mkdir -p /app/data

CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 app:app
