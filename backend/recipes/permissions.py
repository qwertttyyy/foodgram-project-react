from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    """Ограничивает доступ к объекту."""

    def has_permission(self, request, view):
        """Даёт доступ, если пользователь
        авторизован или запрос только на получение данных."""

        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Даёт доступ к объекту, если пользователь является
        создателем объекта или запрос только на получение объекта."""

        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
