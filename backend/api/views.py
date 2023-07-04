from rest_framework import viewsets, mixins, status
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ViewSet, ModelViewSet, GenericViewSet
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.serializers import Serializer
from django.shortcuts import get_object_or_404
from django.db.models import Exists, Q, Count, F, Subquery, OuterRef, Avg, Prefetch
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from djoser.serializers import SetPasswordSerializer

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser

User = get_user_model()


from recipes.models import Recipe, Tag, Ingredient, IngredientInRecipe, ShoppingCart
from recipes.models import FavoriteRecipe, Subscriptions


from .serializers import UserSerializer, SubscriptionsSerializer, \
    ShoppingCartSerializer, FavoriteSerializer
# from .serializers import UserWriteSerializer
from .serializers import TagSerializer
from .serializers import RecipeReadSerializer
from .serializers import RecipeWriteSerializer
from .serializers import RecipeShortSerializer
from .serializers import IngredientSerializer
from .serializers import SubscribeSerialization
from .filters import RecipeFilter, IngredientFilter
from .permissions import IsAdminOrReadOnly, IsAuthenticatedOwnerAdminOrReadOnly


class CreateListRetrieveViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                                mixins.RetrieveModelMixin, GenericViewSet):
    pass


class UserViewSet(CreateListRetrieveViewSet):
    """Пользователи"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):

        queryset = super().get_queryset().annotate(is_subscribed=Exists(
            Subquery(
                Subscriptions.objects.filter(
                    user=self.request.user.id,
                    author=OuterRef("pk")
                )
                # self.request.user.follower.filter(author=OuterRef("pk"))
            )
        ))


        # queryset = super().get_queryset().annotate(is_subscribed=Exists(
        #     Subquery(
        #         self.request.user.follower.filter(author=OuterRef("pk"))
        #     )
        # ))

        if self.action in ('subscriptions', 'subscribe'):
            return queryset.annotate(
                recipes_count=Count('recipes')
            ).prefetch_related('recipes')
        return queryset

    def get_serializer_class(self):
        serializers = {
            'subscriptions': SubscriptionsSerializer,
            'subscribe': SubscribeSerialization,
            'set_password': SetPasswordSerializer
        }
        return serializers.get(self.action, super().get_serializer_class())

    def get_permissions(self):
        if self.action in ('me', 'set_password', 'subscriptions',
                           'subscribe', 'logout'):
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(detail=False)
    def me(self, request, *args, **kwargs):
        """Профиль пользователя"""
        serializer = self.get_serializer(
            self.get_queryset().filter(pk=request.user.id).first()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['post'], detail=False)
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.data["new_password"])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def subscriptions(self, request):
        queryset = self.get_queryset().filter(
            subscriptions__user=self.request.user
        )
        serializer = self.get_serializer(
            self.paginate_queryset(queryset),
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, pk=None):
        author_qs = self.get_queryset().filter(pk=pk)
        if request.method == 'POST':
            serializer = self.get_serializer(
                data={'author': pk, 'user': request.user.id},
                context={'annotated_qs_author': author_qs, 'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        author = self.get_object()
        obj = Subscriptions.objects.filter(user=request.user, author=author)
        if not obj.exists():
            raise ValidationError('Нет подписки на этого автора.')
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = [IsAuthenticatedOwnerAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        if self.action in ('shopping_cart', 'download_shopping_cart'):
            return ShoppingCart.objects.filter(user=self.request.user)
        if self.action == 'favorite':
            return FavoriteRecipe.objects.filter(user=self.request.user)
        # if not self.request.user.is_authenticated:
        #     return super().get_queryset()

        # prefetch = Prefetch(
        #     'author', queryset=User.objects.annotate(
        #         is_subscribed=Exists(Subquery(
        #             self.request.user.follower.filter(author=OuterRef("pk"))
        #         ))
        #     )
        # )

        filter_user_recipe = {
            'user': self.request.user.id,
            'recipe': OuterRef("pk")
        }

        prefetch = Prefetch(
            'author', queryset=User.objects.annotate(
                is_subscribed=Exists(Subquery(
                    Subscriptions.objects.filter(
                        user=self.request.user.id,
                        author=OuterRef("pk")
                    )
                ))
            )
        )

        queryset = super().get_queryset().annotate(
            is_favorited=Exists(
                Subquery(FavoriteRecipe.objects.filter(**filter_user_recipe))
            ),
            is_in_shopping_cart=Exists(
                Subquery(ShoppingCart.objects.filter(**filter_user_recipe))
            )
        ).prefetch_related(prefetch, 'ingredients', 'tags')
        return queryset



        # queryset = super().get_queryset().annotate(
        #     is_favorited=Exists(
        #         Subquery(self.request.user.favoriterecipe_set.filter(
        #             recipe=OuterRef('pk')
        #         ))
        #     ),
        #     is_in_shopping_cart=Exists(
        #         Subquery(self.request.user.shoppingcart_set.filter(
        #             recipe=OuterRef('pk')
        #         ))
        #     )
        # ).prefetch_related(prefetch, 'ingredients', 'tags')
        # return queryset

    def get_serializer_class(self):
        serializers = {
            'download_shopping_cart': RecipeShortSerializer,
            'shopping_cart': ShoppingCartSerializer,
            'favorite': FavoriteSerializer,
            'create': RecipeWriteSerializer,
            'update': RecipeWriteSerializer,
            'partial_update': RecipeWriteSerializer
        }
        return serializers.get(self.action, super().get_serializer_class())

    def get_permissions(self):
        permissions = {
            'download_shopping_cart': [IsAuthenticated]
        }
        self.permission_classes = permissions.get(self.action,
                                                  self.permission_classes)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False) #, url_path='download_shopping_cart'
    def download_shopping_cart(self, request):
        qs = Recipe.objects.filter(
            id__in=self.get_queryset().values_list('recipe__id', flat=True)
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
    #  TODO доделать

    def __create_destroy_recipes(self, request, pk):
        if request.method == "POST":
            serializer = self.get_serializer(
                data={'user': request.user.id, 'recipe': pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        recipe = get_object_or_404(Recipe, pk=pk)
        obj = self.get_queryset().filter(recipe=recipe)

        if not obj.exists():
            raise ValidationError(
                f'Этого рецепта нет '
                f'в {self.get_queryset().model._meta.verbose_name_plural}.'
            )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        return self.__create_destroy_recipes(request, pk)

    @action(['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        return self.__create_destroy_recipes(request, pk)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(TagViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter






# TODO ингредиенты
# TODO почистить селфы в актио.нах








