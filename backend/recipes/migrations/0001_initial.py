# Generated by Django 3.2 on 2023-06-24 15:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'name',
                    models.CharField(
                        db_index=True, max_length=200, verbose_name='Название'
                    ),
                ),
                (
                    'measurement_unit',
                    models.CharField(max_length=200, verbose_name='Мера'),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'name',
                    models.CharField(max_length=200, verbose_name='Название'),
                ),
                ('text', models.TextField(verbose_name='Описание')),
                ('image', models.ImageField(upload_to='recipes/images')),
                (
                    'cooking_time',
                    models.PositiveSmallIntegerField(
                        verbose_name='Время приготовления'
                    ),
                ),
                (
                    'created',
                    models.DateTimeField(
                        auto_now_add=True, verbose_name='Дата публикации'
                    ),
                ),
                (
                    'author',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='recipes',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Автор',
                    ),
                ),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'name',
                    models.CharField(
                        max_length=200, unique=True, verbose_name='Название'
                    ),
                ),
                (
                    'color',
                    models.CharField(
                        max_length=7, unique=True, verbose_name='Цвет'
                    ),
                ),
                (
                    'slug',
                    models.SlugField(
                        max_length=200, unique=True, verbose_name='Слаг'
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='RecipeTag',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'recipe',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='recipes.recipe',
                    ),
                ),
                (
                    'tag',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='recipes.tag',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('amount', models.PositiveIntegerField(verbose_name='Кол-во')),
                (
                    'ingredient',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='recipes.ingredient',
                    ),
                ),
                (
                    'recipe',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='recipe_ingredients',
                        to='recipes.recipe',
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(
                through='recipes.RecipeIngredient',
                to='recipes.Ingredient',
                verbose_name='Ингридиенты',
            ),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(
                through='recipes.RecipeTag',
                to='recipes.Tag',
                verbose_name='Теги',
            ),
        ),
    ]
