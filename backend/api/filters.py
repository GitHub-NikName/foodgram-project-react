from django.db.models import BooleanField, ExpressionWrapper, Q, QuerySet
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter()
    is_in_shopping_cart = filters.BooleanFilter()

    class Meta:
        model = Recipe
        fields = ('tags', 'author')


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', method='filter_name')

    def filter_name(self, queryset: QuerySet, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).annotate(
            is_start=ExpressionWrapper(
                Q(name__istartswith=value),
                output_field=BooleanField()
            )
        ).order_by('-is_start', 'name')

    class Meta:
        model = Ingredient
        fields = ['name']
