from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name='Название'
    )
    color = models.CharField(max_length=7, unique=True, verbose_name='Цвет')
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name='Слаг', db_index=True
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Название', db_index=True
    )
    measurement_unit = models.CharField(max_length=200, verbose_name='Мера')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='recipes/images')
    tags = models.ManyToManyField(
        Tag, through='RecipeTag', verbose_name='Теги'
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='Ингридиенты'
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return ' {0} - {1}'.format(self.recipe.name, self.tag.name)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.SET_NULL, null=True
    )
    amount = models.PositiveIntegerField(verbose_name='Кол-во')

    def __str__(self):
        return '{0} - {1}'.format(self.recipe.name, self.ingredient.name)
