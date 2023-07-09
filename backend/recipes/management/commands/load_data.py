import json
from pathlib import PosixPath

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

PATH_FILES = settings.BASE_DIR.parent.joinpath('data')


def open_file(file: PosixPath) -> list[dict | str]:
    try:
        if file.name.endswith('.json'):
            return json.load(file.open(encoding='utf-8'))
        return [i.strip() for i in file.read_text(encoding='utf-8').split(',')]
    except FileNotFoundError:
        print('Файл %s не найден.' % file.as_posix())


def load_json_files(files: list[PosixPath]) -> None:
    for file in files:
        cls = FILES_CLASSES[file.name.split('.')[0]]
        not_loaded = 'Файл %s не загружен.' % file.name
        loaded = 'Файл %s загружен.' % file.name
        if cls.objects.exists():
            print(f'В таблице {cls.__name__} уже есть данные.', not_loaded)
            continue
        try:
            objects = [cls(**el) for el in open_file(file)]
            cls.objects.bulk_create(objects)
            print(loaded)
        except (ValueError, IntegrityError) as exc:
            print('Ошибка в загружаемых данных %s' % exc, not_loaded)


def save_json(data: list[dict]) -> None:
    file = PATH_FILES.joinpath('tags.json')
    json.dump(data, file.open('w', encoding='utf-8'), ensure_ascii=False)
    print('Теги сохранены в файл %s' % file.as_posix())


def gen_tags() -> None:
    if Tag.objects.exists():
        print('В таблице уже есть данные. Теги не загружены')
        return
    print('генерируем теги.')
    tags_list_path = PATH_FILES.joinpath('tags.txt')
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
        json_files = list(PATH_FILES.glob('*.json'))
        load_json_files(json_files)
        if PATH_FILES.joinpath('tags.json') not in json_files:
            print('файл tags.json не найден')
            gen_tags()
