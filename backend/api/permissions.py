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
