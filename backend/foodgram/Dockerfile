FROM python:3.7-slim
LABEL website='https://github.com/EISerova/api-yamdb'
LABEL desc='This source create for studing'
LABEL email='katyaserova@yandex.ru'

# ENV PYTHONUNBUFFERED 1

WORKDIR /app
# COPY . .
ADD requirements.txt /app/
RUN pip3 install -r requirements.txt
ADD . /app/

# WORKDIR /app
# COPY requirements.txt /app

# RUN pip3 install -r /app/requirements.txt --no-cache-dir
# COPY ./ /app


# ADD . /code/
# RUN pip install -r /code/requirements/docker.txt
# Это ваша проблема-Docker проверяет каждый оператор ADD, чтобы увидеть, если какие-либо файлы изменились и аннулирует кэш для него и каждый последующий шаг, если он имеет. Правильный способ сделать это...

# ADD ./requirements/docker.txt /code/requirements/
# RUN pip install -r /code/requirements/docker.txt
# ADD ./code/