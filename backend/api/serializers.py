from collections import OrderedDict
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField
from djoser.serializers import UserCreateSerializer

from recipes.models import (
    Recipe,
    Subscriptions
)
from recipes.models import (
    Tag,
    Ingredient,
    IngredientInRecipe,
    FavoriteRecipe,
    ShoppingCart
)
from .utils import (
    create_list_obj,
    empty_validator,
    DynamicUniqueTogetherValidator
)


User = get_user_model()


class UserSerializer(UserCreateSerializer):
    """Регистрация и представление пользователей"""
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password', 'is_subscribed')


class TagSerializer(serializers.ModelSerializer):
    """Теги"""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Ингредиенты"""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Ингредиенты - рецепты"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        exclude = ('recipe', 'ingredient')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Рецепты (чтение)"""
    tags = TagSerializer(many=True)
    author = UserSerializer(default=serializers.CurrentUserDefault())
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredientinrecipe_set',
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ('created',)


class RecipeWriteSerializer(RecipeReadSerializer):
    """Рецепты (запись)"""
    tags = serializers.ManyRelatedField(
        child_relation=serializers.PrimaryKeyRelatedField(
            queryset=Tag.objects.all()
        ),
        validators=[empty_validator]
    )

    def validate_ingredients(self, value):
        empty_validator(value)
        if len(value) != len(set([i['ingredient'].id for i in value])):
            raise serializers.ValidationError('Рецепты повторяются.')
        return value

    def create(self, validated_data: dict) -> Recipe:
        ingredients = validated_data.pop('ingredientinrecipe_set')
        tags = validated_data.pop('tags')

        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            recipe.tags.set(tags)
            IngredientInRecipe.objects.bulk_create(
                create_list_obj(IngredientInRecipe, ingredients, recipe=recipe)
            )
        return recipe

    def update(self, instance: Recipe, validated_data: OrderedDict):
        if 'ingredientinrecipe_set' in validated_data:
            ingredients = validated_data.pop('ingredientinrecipe_set')

            with transaction.atomic():
                instance.ingredientinrecipe_set.all().delete()
                IngredientInRecipe.objects.bulk_create(
                    create_list_obj(IngredientInRecipe, ingredients,
                                    recipe=instance)
                )

        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)

        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance: Recipe):
        try:
            annotated_instance = self.context['view'].get_queryset().filter(
                pk=instance.pk).first()
        except Exception as e:
            raise ValueError(e)
        return RecipeReadSerializer(
            annotated_instance, context={'request': self.context['request']}
        ).data


class RecipeShortSerializer(RecipeReadSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [DynamicUniqueTogetherValidator(model)]

    def to_representation(self, instance: ShoppingCart):
        return RecipeShortSerializer(instance.recipe).data


class FavoriteSerializer(ShoppingCartSerializer):

    class Meta(ShoppingCartSerializer.Meta):
        model = FavoriteRecipe
        validators = [DynamicUniqueTogetherValidator(model)]


class SubscriptionsSerializer(UserSerializer):
    """Подписки"""
    recipes = RecipeShortSerializer(many=True)
    recipes_count = serializers.IntegerField()

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password', 'is_subscribed', 'recipes', 'recipes_count')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        try:
            limit = self.context['request'].query_params.get('recipes_limit')
            if limit:
                ret['recipes'] = ret['recipes'][:int(limit)]
        except Exception as e:
            raise ValueError(e)
        return ret


class SubscribeSerialization(serializers.ModelSerializer):
    """Подписки для записи"""
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Subscriptions
        fields = '__all__'
        validators = [DynamicUniqueTogetherValidator(model)]

    def validate_author(self, author):
        if self.context['request'].user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя.'
            )
        return author

    def to_representation(self, instance: Subscriptions):
        try:
            annotated_author = self.context['annotated_qs_author'].first()
        except Exception as e:
            raise ValueError(e, 'annotated_qs_author not in context')
        assert annotated_author == instance.author
        return SubscriptionsSerializer(
            annotated_author, context={'request': self.context['request']}
        ).data
