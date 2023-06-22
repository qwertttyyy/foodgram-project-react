import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.models import Recipe, Tag, RecipeIngredient, Ingredient
from api.serializers import TagSerializer
from users.serializers import CustomUserSerializer


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
            serializers.ValidationError('Количество должно быть больше нуля')
        return amount


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_, img_str = data.split(';base64,')
            ext = format_.split('/')[-1]

            data = ContentFile(base64.b64decode(img_str), name='temp.' + ext)

        return super().to_internal_value(data)


class TagIDListField(serializers.ListField):
    child = serializers.IntegerField()

    def to_internal_value(self, data):
        ids = super().to_internal_value(data)
        tags = Tag.objects.filter(id__in=ids)
        return tags

    def to_representation(self, data):
        return TagSerializer(data, many=True).data


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    tags = TagIDListField(required=True)

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
        for item in recipe_ingredient_set:
            get_object_or_404(Ingredient, id=item['ingredient']['id'])
        return recipe_ingredient_set

    def update(self, recipe, validated_data):
        recipe_ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.image = validated_data.get('image', recipe.image)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time
        )
        recipe.save()

        for tag in recipe.tags.all():
            recipe.tags.remove(tag)
        for tag in tags:
            recipe.tags.add(tag)

        recipe.recipe_ingredients.all().delete()

        for ingredient_and_amount in recipe_ingredients:
            ingredient_id = ingredient_and_amount['ingredient']['id']
            amount = ingredient_and_amount['amount']
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient_id=ingredient_id, amount=amount
            )

        return recipe

    def create(self, validated_data):
        recipe_ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            recipe.tags.add(tag)

        for ingredient_and_amount in recipe_ingredients:
            ingredient_id = ingredient_and_amount['ingredient']['id']
            amount = ingredient_and_amount['amount']
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient_id=ingredient_id, amount=amount
            )

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
