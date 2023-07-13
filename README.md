# Продуктовый помощник  Foodgram


Доменное имя: foodgram.didns.ru


## Описание

Платформа для обмена рецептами


### Технологии
- Python 3.11
- Django 4.2
- DRF 3.12
- Postgres
- Docker

### Как запустить проект:
- Клонировать репозиторий и перейти в него в командной строке:

```bash
https://github.com/sergeev-m/foodgram-project-react.git
cd foodgram-project-react
```

- Запустить
```bash
docker-compose up -d
````

### Загрузить в базу теги, ингредиенты, рецепты из /data/
Для загрузки рецептов должен быть создан пользователь.
```bash
python manage.py load_data
python manage.py load_recipes
```

### Контакты

Михаил  
[email](server-15@yandex.ru)  
[telegram](https://t.me/sergeev_mikhail)
