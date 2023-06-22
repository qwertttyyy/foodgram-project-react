from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата оформления подписки'
    )

    class Meta:
        ordering = ('-created',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'), name='unique_follow'
            ),
        )
