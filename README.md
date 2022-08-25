# Foodgram - домашний кулинар.
![example workflow](https://github.com/EISerova/foodgram-project-react/actions/workflows/main.yml/badge.svg)  
![DjangoREST](https://img.shields.io/badge/-Django-green) ![Docker](https://img.shields.io/badge/-Docker-yellowgreen) ![Nginx](https://img.shields.io/badge/-Nginx-lightgrey)

**Foodgram** - сервис для поиска вкусных рецептов. Он также составит для Вас список покупок, необходимых для готовки. А если Вы хотите похвалиться любимых бабушкиным рецептом, то можете его опубликовать в Foodgram и получить признание от подписчиков.

**Адрес**: http://51.250.108.117/

тестовый юзер: 
ddd@dd.ru
87654321AA

тестовый админ:
admin
12345


### Запуск проекта в Docker

Настройки базы по умолчанию:
* ENGINE = django.db.backends.postgresql
* NAME = postgres
* USER = postgres
* PASSWORD = 12345
* HOST = db
* PORT = 5432

Запустить контейнер
```
docker-compose up -d --build
```
Войти в контейнер командой:
```
docker exec -it foodgram bash
```
Применить миграции:
```
python manage.py migrate
```
Собрать статику:
```
python manage.py collectstatic
```

### Техническое описание проекта:
На странице с документацией [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/) можно ознакомиться с примерами запросов и ответов на них.


#### Автор - [Екатерина Серова](https://github.com/EISerova/)
Если у вас есть предложения или замечания, пожалуйста, свяжитесь со мной - [katyaserova@yandex.ru]

Лицензия:
[MIT](https://choosealicense.com/licenses/mit/)
