from typing import Any

from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import validate_slug
from django.utils.translation import gettext_lazy as _

from .validators import validate_cooking_time_min, validate_ingredient_amount_min
from django.conf import settings

User = get_user_model()


class Base(models.Model):
    # def __str__(self):
    #     pass

    def __repr__(self):
        return self.__str__()

    class Meta:
        abstract = True


class RecipeMixin(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )


class UserMixin(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
    )


def get_constrains(fields: list, cls_name: str) -> list[Any]:
    return [
        models.UniqueConstraint(
                fields=fields,
                name='user_recipe_%s' % cls_name
            ),
    ]


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.TAG_NAME_MAX_LENGTH,
        unique=True
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=settings.TAG_COLOR_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=settings.TAG_SLUG_MAX_LENGTH,
        unique=True,
        validators=[validate_slug],
        db_index=True
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return "%s(%s, %s)" % (type(self).__name__, self.pk, self.name)

    def __repr__(self):
        return self.__str__()


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=settings.INGREDIENT_NAME_MAX_LENGTH,
        db_index=True
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.RECIPE_NAME_MAX_LENGTH
    )
    text = models.TextField('Описание')
    tags = models.ManyToManyField(Tag, verbose_name='Список тегов')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    image = models.ImageField(
        'Ссылка на картинку на сайте',
        upload_to='recipes/images/'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Список ингредиентов'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[validate_cooking_time_min]
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return "%s(%s, %s)" % (self.__class__.__name__, self.pk, self.name)


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[validate_ingredient_amount_min]
    )

    def __str__(self):
        return "%s(%s, %s)" % (
            self.__class__.__name__, self.ingredient, self.recipe
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = get_constrains(['user', 'recipe'], 'shoppingcart')
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзине покупок'

    def __str__(self):
        return '%s(%s, %s, %s)' % (
            type(self).__name__, self.pk, self.user, self.recipe
        )

    def __repr__(self):
        return self.__str__()


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = get_constrains(['user', 'recipe'], 'favoriterecipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранном'

    def __str__(self):
        return '%s(%s, %s, %s)' % (
            type(self).__name__, self.pk, self.user, self.recipe
        )

    def __repr__(self):
        return self.__str__()


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = get_constrains(['user', 'author'], 'subscriptions')
