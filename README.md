# FOODGRAM
<!-- ![example workflow](https://github.com/EISerova/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)   -->
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)


### Описание:
База отзывов на книги и музыку, доступ через API. Пользователи могут делиться мнением, оценивать произведения, смотреть отзывы других. 
Учебный проект, созданный в рамках учебы в Яндекс.Практикуме. Проект развернут по адресу: http://bento.sytes.net/

### Техническое описание проекта:
На странице с документацией localhost/redoc/ можно ознакомиться с примерами запросов и ответов на них.

### Зависимости:
Python 3.8  
Django 3.0
Django rest framework 3.12

## Примеры API-запросов:

#### Получение списка всех произведений

```http
  GET /api/v1/titles/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `token`   | `string` | **Required**. Ваш токен    |

#### Добавление нового отзыва к произведению

```http
  POST /api/v1/titles/{id}/reviews/
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `token`   | `string` | **Required**. Ваш токен           |
| `id`      | `string` | **Required**. Id произведения     |
| `text`    | `string` | **Required**. Текст отзыва        |
| `score`   | `integer` | **Required**. Оценка произведения |


### Запуск проекта в Docker

Запустить контейнер
```power shell
  docker-compose up -d --build
```

Импортировать данные в формате json (список ингредиентов и тэгов из папки Data)
```power shell
  docker-compose exec web python manage.py import_json
```

### Автор: 
- [Екатерина Серова](https://github.com/EISerova/).


### Обратная связь:
Если у вас есть предложения или замечания, пожалуйста, свяжитесь со мной - katyaserova@yandex.ru

### Лицензия:
[MIT](https://choosealicense.com/licenses/mit/)