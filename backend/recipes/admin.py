from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Subscriptions, Tag,)


class IngredientsInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientsInline]
    readonly_fields = ('author', 'show_favorite_count')
    list_display = ('name', 'author')
    search_fields = ('author__username', 'name', 'tags__slug')
    list_filter = ('author__username', 'name', 'tags__slug')

    @admin.display(description='В избранном')
    def show_favorite_count(self, obj: Recipe):
        return obj.favoriterecipe_set.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(IngredientInRecipe)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Subscriptions)
