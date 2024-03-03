# Используем официальный образ Python как базовый
FROM python:3.10.7

# Устанавливаем рабочую директорию в контейнере
WORKDIR /studyforge

# Копируем файлы проекта в контейнер
COPY . /studyforge

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Сообщаем Docker, что контейнер будет слушать на порту 8000
EXPOSE 8000

# Запускаем Gunicorn с нашим приложением Flask
CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app"]
