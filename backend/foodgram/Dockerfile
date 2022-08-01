FROM python:3.7-slim
LABEL website='https://github.com/EISerova/api-yamdb'
LABEL desc='This source create for studing'
LABEL email='katyaserova@yandex.ru'

ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY ./ /app

