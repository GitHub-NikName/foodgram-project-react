from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from .load_data import PATH_FILES, open_file

User = get_user_model()

user = User.objects.get(id=1)
recipes = open_file(PATH_FILES.joinpath('recipes_soups.json'))


def load_recipes():
    recipes_list = [
        Recipe(
            name=i['name'],
            text=i['text'],
            image=i['image'],
            cooking_time=i['cooking_time'],
            author=user) for i in recipes
    ]
    recipes_obj = Recipe.objects.bulk_create(recipes_list)
    tags = Tag.objects.filter(slug__in=['uzhin', 'sup'])
    for i in recipes_obj:
        i.tags.set(tags)

    ingredients = [i['ingredients'] for i in recipes]
    for i in range(len(ingredients)):
        recipe = recipes_obj[i]
        ingredients_data = ingredients[i]
        for j in ingredients_data:
            ingredient, _ = Ingredient.objects.get_or_create(
                name=j['name'], measurement_unit=j['measurement_unit']
            )
            IngredientInRecipe.objects.create(
                ingredient=ingredient, recipe=recipe, amount=j['amount']
            )


class Command(BaseCommand):

    def handle(self, *args, **options):
        load_recipes()
