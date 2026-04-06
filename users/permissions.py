from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Разрешение для модераторов.
    Проверяет, состоит ли пользователь в группе "Модераторы".
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Модераторы').exists()


class IsOwner(permissions.BasePermission):
    """
    Разрешение для владельца объекта.
    Проверяет, является ли пользователь владельцем объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Проверяем, что пользователь авторизован и является владельцем
        return request.user.is_authenticated and obj.owner == request.user
