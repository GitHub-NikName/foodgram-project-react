import random

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from .load_data import PATH_FILES, open_file

User = get_user_model()

user = User.objects.get(id=1)
file_name = 'recipes.json'
recipes = open_file(PATH_FILES.joinpath(file_name))


def load_recipes():
    if IngredientInRecipe.objects.exists():
        print(f'В таблице {IngredientInRecipe.__name__} уже есть данные.')
        print('Загрузка %s не выполнена' % file_name)
        return

    print('Загрузка рецептов из %s' % file_name)
    print('%s рецептов' % len(recipes))
    recipes_list = [
        Recipe(
            name=i['name'],
            text=i['text'],
            image='recipes/images/' + i['image'],
            cooking_time=i['cooking_time'],
            author=user) for i in recipes
    ]
    recipes_obj = Recipe.objects.bulk_create(recipes_list)
    all_tags = Tag.objects.values_list('slug', flat=True)
    tags_image = {i['name']: i['image'] for i in recipes}
    for recipe in recipes_obj:
        tags = [tag for tag in all_tags if tag in tags_image[recipe.name]]
        if not tags:
            tags = [random.choice(['завтрак', 'обед', 'ужин', []])]
        tags = Tag.objects.filter(slug__in=tags)
        recipe.tags.set(tags)

    ingredients_in_recipes = []
    for i in range(len(recipes)):
        recipe = recipes_obj[i]
        ingredients = recipes[i]['ingredients']

        for j in ingredients:
            ingredient, _ = Ingredient.objects.get_or_create(
                name=j['name'], measurement_unit=j['measurement_unit']
            )
            ingredients_in_recipes.append(
                IngredientInRecipe(
                    ingredient=ingredient, recipe=recipe, amount=j['amount']
                )
            )
    IngredientInRecipe.objects.bulk_create(ingredients_in_recipes)
    print('Рецепты из %s загружены' % file_name)


class Command(BaseCommand):

    def handle(self, *args, **options):
        load_recipes()
