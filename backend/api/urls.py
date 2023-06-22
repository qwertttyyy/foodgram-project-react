from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, TagViewSet

router = DefaultRouter()

router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)


urlpatterns = [path('', include(router.urls))]
