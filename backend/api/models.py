from django.db import models

from recipes.models import Recipe
from users.models import User


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorites'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorite'
            ),
        )

    def __str__(self):
        return '{0} - {1}'.format(self.recipe.name, self.user.username)


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_shopping_cart'
            ),
        )

    def __str__(self):
        return '{0} - {1}'.format(self.recipe.name, self.user.username)
