from urllib.parse import unquote

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import RecipeFilter
from api.pagination import RecipesPagination, UsersPagination
from api.permissions import (
    ReadOnly,
    OwnerOrReadOnly,
    IsRetrieveAuthenticatedOrReadOnly,
)
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ReducedRecipeSerializer,
    FollowSerializer,
)
from api.utilities import create_shopping_list, generate_shopping_list_pdf
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from users.models import Follow, User


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (ReadOnly,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (ReadOnly,)
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        search_name = self.request.GET.get('name')
        if search_name:
            decoded_name = unquote(search_name)
            queryset = queryset.filter(name__istartswith=decoded_name)
        return queryset


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
                recipes = recipes.filter(favorites__user=user)
            else:
                recipes = recipes.exclude(favorites__user=user)

        if is_in_shopping_cart:
            is_in_shopping_cart_value = bool(int(is_in_shopping_cart))
            if is_in_shopping_cart_value:
                recipes = recipes.filter(shoppingcart__user=user)
            else:
                recipes = recipes.exclude(shoppingcart__user=user)

        return recipes

    def add_or_remove_recipe(self, request, recipe, model, instance):
        is_exists = instance.exists()
        if request.method == 'POST':
            if is_exists:
                return Response(
                    {'error': 'Рецепт уже добавлен'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            obj = model(user=request.user, recipe=recipe)
            obj.save()
            serializer = ReducedRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not is_exists:
            return Response(
                {'errors': 'Рецепт ещё не добавлен'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = request.user.favorites.filter(recipe=recipe)
        return self.add_or_remove_recipe(request, recipe, Favorite, favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_cart = request.user.shopping_cart.filter(recipe=recipe)
        return self.add_or_remove_recipe(
            request, recipe, ShoppingCart, shopping_cart
        )

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_cart = Recipe.objects.filter(shoppingcart__user=request.user)
        shopping_list = create_shopping_list(shopping_cart)
        filename = f'{request.user.username}_shopping_list.pdf'
        file = generate_shopping_list_pdf(shopping_list)
        response = HttpResponse(file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsRetrieveAuthenticatedOrReadOnly,)
    pagination_class = UsersPagination

    def get_queryset(self):
        paginator = self.paginate_queryset(
            self.queryset.order_by('-date_joined')
        )
        return paginator

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        follows = Follow.objects.filter(following=request.user)
        followers = User.objects.filter(
            id__in=follows.values('user')
        ).order_by('-follower__created')
        paginator = self.paginate_queryset(followers)
        serializer = FollowSerializer(
            paginator, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        follower = request.user
        following = get_object_or_404(User, id=id)
        follow = Follow.objects.filter(user=following, following=follower)
        if request.method == 'POST':
            if follower == following or follow.exists():
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            follow = Follow(user=following, following=follower)
            follow.save()
            serializer = FollowSerializer(
                following, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not follow.exists():
            return Response(
                {'errors': 'Ошибка отписки'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
