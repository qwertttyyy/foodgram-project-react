from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReadOnly(BasePermission):
    """Права доступа только чтение."""

    def has_permission(self, request, view) -> bool:
        del view
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj) -> bool:
        del view
        del obj
        return request.method in SAFE_METHODS


class IsRetrieveAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'retrieve' or view.action == 'me':
            return request.user.is_authenticated
        return request.method in SAFE_METHODS


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
