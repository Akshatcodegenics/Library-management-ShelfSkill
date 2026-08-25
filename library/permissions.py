from rest_framework import permissions
from accounts.models import UserRole


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access for all users; write access ONLY to Administrators.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == UserRole.ADMIN or request.user.is_staff or request.user.is_superuser


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in [UserRole.AUTHOR, UserRole.ADMIN] or request.user.is_staff


class IsBookOwnerAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in [UserRole.AUTHOR, UserRole.ADMIN] or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.role == UserRole.ADMIN or request.user.is_staff:
            return True
        if hasattr(obj.author, 'user') and obj.author.user:
            return obj.author.user == request.user
        return obj.author.email == request.user.email


class IsMemberSelfOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.ADMIN or request.user.is_staff:
            return True
        if hasattr(obj, 'user') and obj.user:
            return obj.user == request.user
        return obj.email == request.user.email
