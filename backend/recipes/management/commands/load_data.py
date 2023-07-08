import json
import os

import rstr
from django.conf import settings
from django.core.management import BaseCommand
from django.db import IntegrityError
from transliterate import slugify

from recipes.models import Ingredient, Tag

FILES_CLASSES = {
    'ingredients': Ingredient,
    'tags': Tag,
}

PATH_FILES = os.path.join(settings.BASE_DIR.parent, 'data')


def open_file(file_name: str) -> list[dict | str]:
    path = os.path.join(PATH_FILES, file_name)
    try:
        with open(path, encoding='utf-8') as file:
            if path.endswith('.json'):
                return json.load(file)
            return [i.strip() for i in file.read().split(',')]
    except FileNotFoundError:
        print('Файл %s не найден.' % path)


def load_json_files(json_files: list[str]):
    for file_name in json_files:
        cls = FILES_CLASSES[file_name.split('.')[0]]
        not_loaded = 'Файл %s не загружен.' % file_name
        loaded = 'Файл %s загружен.' % file_name
        if cls.objects.exists():
            print(f'В таблице {cls.__name__} уже есть данные.', not_loaded)
            continue
        try:
            objects = [cls(**el) for el in open_file(file_name)]
            cls.objects.bulk_create(objects)
            print(loaded)
        except (ValueError, IntegrityError) as exc:
            print('Ошибка в загружаемых данных %s' % exc, not_loaded)


def save_json(data):
    path_file = os.path.join(PATH_FILES, 'tags.json')
    with open(path_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)
    print('Теги сохранены в файл %s' % path_file)


def gen_tags():
    if Tag.objects.exists():
        print('В таблице уже есть данные. Теги не загружены')
        return
    print('генерируем теги.')
    tags_list_path = os.path.join(PATH_FILES, 'tags.txt')
    tags = open_file(tags_list_path)
    slugs = [slugify(tag, language_code='ru') for tag in tags]
    colors = []
    while len(colors) < len(tags):
        hex_code = rstr.xeger('^#(?:[0-9a-fA-F]{3}){1,2}$')
        if hex_code not in colors:
            colors.append(hex_code)

    message = 'данные не уникальны'
    assert len(tags) == len(set(tags)), message
    assert len(slugs) == len(set(slugs)), message

    keys = ['name', 'slug', 'color']
    tags_data = [dict(zip(keys, i)) for i in zip(tags, slugs, colors)]
    try:
        Tag.objects.bulk_create([Tag(**i) for i in tags_data])
        print('Теги сгенерированы и загружены.')
    except IntegrityError as exc:
        print('Ошибка загрузки данных %s' % exc)
    save_json(tags_data)


class Command(BaseCommand):

    def handle(self, *args, **options):
        json_files = [i for i in os.listdir(PATH_FILES) if i.endswith('.json')]
        load_json_files(json_files)
        if 'tags.json' not in json_files:
            print('файл tags.json не найден')
            gen_tags()
