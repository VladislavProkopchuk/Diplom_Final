FROM python:3.10-slim

# Установка необходимых пакетов, обновление pip
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py makemigrations
RUN python manage.py migrate

# Порт
EXPOSE 8000

CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:8000", "final.wsgi:application"]