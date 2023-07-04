from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import Tag, Ingredient, RecipeIngredient, Recipe
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', required=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError(
                'Количество должно быть больше нуля'
            )
        return amount


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', required=True, many=True
    )
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )
        extra_kwargs = {
            'name': {'required': True},
            'text': {'required': True},
            'cooking_time': {'required': True},
            'image': {'required': True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        return representation

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления не должно быть меньше одной минуты'
            )
        return cooking_time

    def get_author(self, recipe):
        author_data = CustomUserSerializer(
            recipe.author, context=self.context
        ).data
        author_data['id'] = recipe.author.id
        return author_data

    def validate_ingredients(self, recipe_ingredient_set):
        ingredients_ids = [
            ingredient['ingredient']['id']
            for ingredient in [item for item in recipe_ingredient_set]
        ]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                'В рецепте не должно быть одинаковых ингредиентов'
            )
        return recipe_ingredient_set

    def create_recipe_ingredients(self, recipe, recipe_ingredients):
        recipe_ingredients_data = []

        for ingredient_and_amount in recipe_ingredients:
            ingredient_id = ingredient_and_amount['ingredient']['id']
            amount = ingredient_and_amount['amount']
            recipe_ingredients_data.append(
                RecipeIngredient(
                    recipe=recipe, ingredient_id=ingredient_id, amount=amount
                )
            )

        RecipeIngredient.objects.bulk_create(recipe_ingredients_data)

    def update(self, recipe, validated_data):
        recipe_ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        super().update(recipe, validated_data)

        for tag in recipe.tags.all():
            recipe.tags.remove(tag)
        for tag in tags:
            recipe.tags.add(tag)

        recipe.recipe_ingredients.all().delete()
        self.create_recipe_ingredients(recipe, recipe_ingredients)

        return recipe

    def create(self, validated_data):
        recipe_ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            recipe.tags.add(tag)

        self.create_recipe_ingredients(recipe, recipe_ingredients)

        return recipe

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorites.filter(recipe=recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping_cart.filter(recipe=recipe).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, following):
        follower = self.context.get('request').user
        if follower.is_authenticated:
            return follower.following.filter(user=following).exists()
        return False


class ReducedRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, instance):
        return instance.recipes.count()

    def get_recipes(self, instance):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = instance.recipes.all()[: int(recipes_limit)]
        else:
            recipes = instance.recipes.all()
        serializer = ReducedRecipeSerializer(recipes, many=True)
        return serializer.data
