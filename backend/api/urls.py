from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    TagViewSet,
    CustomUserViewSet,
    RecipeViewSet,
)

router = DefaultRouter()

router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'recipes', RecipeViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
