FROM python:3.7-slim
LABEL website='https://github.com/EISerova/foodgram-project-react'
LABEL desc='This source create for studing'
LABEL email='katyaserova@yandex.ru'


WORKDIR /app
COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY ./ /app
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
