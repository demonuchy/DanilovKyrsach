# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Используем pip для установки
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .
