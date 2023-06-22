import os

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import (
    Recipe,
    Favorite,
    ShoppingCart,
)
from recipes.constants import CACHE_PATH
from recipes.filters import RecipeFilter
from recipes.pagination import RecipesPagination
from recipes.permissions import OwnerOrReadOnly
from recipes.serializers import RecipeSerializer
from recipes.utilities import create_shopping_list, generate_shopping_list_pdf
from users.serializers import ReducedRecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (OwnerOrReadOnly,)
    pagination_class = RecipesPagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        query_params = self.request.query_params
        recipes = self.queryset
        user = self.request.user

        is_favorited = query_params.get('is_favorited')
        is_in_shopping_cart = query_params.get('is_in_shopping_cart')

        if is_favorited:
            is_favorited_value = bool(int(is_favorited))
            if is_favorited_value:
                recipes = recipes.filter(favorite__user=user)
            else:
                recipes = recipes.exclude(favorite__user=user)

        if is_in_shopping_cart:
            is_in_shopping_cart_value = bool(int(is_in_shopping_cart))
            if is_in_shopping_cart_value:
                recipes = recipes.filter(shoppingcart__user=user)
            else:
                recipes = recipes.exclude(shoppingcart__user=user)

        return recipes

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = request.user.favorites.filter(recipe=recipe)
        if request.method == 'POST':
            if favorite:
                return Response(
                    {'error': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            favorite = Favorite(user=request.user, recipe=recipe)
            favorite.save()
            serializer = ReducedRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not favorite:
            return Response(
                {'errors': 'Рецепт не добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_cart = request.user.shopping_cart.filter(recipe=recipe)
        if request.method == 'POST':
            if shopping_cart:
                return Response(
                    {'error': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            shopping_cart = ShoppingCart(user=request.user, recipe=recipe)
            shopping_cart.save()
            serializer = ReducedRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not shopping_cart:
            return Response(
                {'errors': 'Рецепт не добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_cart = Recipe.objects.filter(shoppingcart__user=request.user)
        shopping_list = create_shopping_list(shopping_cart)
        filename = f'{request.user.username}_shopping_list.pdf'
        generate_shopping_list_pdf(shopping_list, filename)
        filepath = os.path.join(CACHE_PATH, filename)
        with open(filepath, 'rb') as file:
            response = HttpResponse(file, content_type='application/pdf')
            response[
                'Content-Disposition'
            ] = f'attachment; filename={filename}'
            return response
