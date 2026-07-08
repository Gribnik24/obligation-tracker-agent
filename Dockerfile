FROM python:3.12-slim

# Устанавливаем локаль ru_RU для корректной работы get_current_time
RUN apt-get update && apt-get install -y --no-install-recommends locales \
    && echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=ru_RU.UTF-8
ENV LC_ALL=ru_RU.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]