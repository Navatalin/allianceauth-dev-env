FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=local_auth.settings.local

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git libmariadb-dev libpq-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY plugins.json install_plugins.py /app/
RUN python -m pip install --no-cache-dir 'allianceauth>=5.4,<6' \
    && python install_plugins.py

WORKDIR /app/allianceauth
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]