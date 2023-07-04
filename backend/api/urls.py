from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet
from .views import TagViewSet
from .views import RecipeViewSet
from .views import IngredientViewSet


app_name = 'api'

v1_router = DefaultRouter()

v1_router.register('users', UserViewSet, basename='users')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns += v1_router.urls



# v1_router.register('categories', CategoriesViewSet, basename='categories')
# v1_router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewVieSet,
#                    basename='review')
# v1_router.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comment'
# )


# urlpatterns = [
    # path('auth/signup/', signup, name='signup'),
    # path('auth/token/',
    #      TokenObtainPairView.as_view(serializer_class=TokenAuthSerializer),
    #      name='token_obtain_pair'),
# ]


#  trailing_slash удаляет конечные /
# v1_router = DefaultRouter(trailing_slash=False)