from django_filters import rest_framework as filters
from django.db.models import Q

from recipes.models import Recipe, Tag, Ingredient


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

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        )

    class Meta:
        model = Ingredient
        fields = ['name']
