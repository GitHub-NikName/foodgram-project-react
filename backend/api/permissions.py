from rest_framework import permissions


class RolePermissions(permissions.BasePermission):
    # allowed_roles = ('user', 'moderator', 'admin')

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_staff
        )


class IsAuthenticatedOwnerAdminOrReadOnly(permissions.BasePermission):
    """ + для автора, админа или только чтение,
    + пост метод для аторизированных пользователей"""

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )
