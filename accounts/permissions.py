from rest_framework import permissions
from .models import UserRole


class IsAdminUserRole(permissions.BasePermission):
    """
    Allows access only to authenticated administrators.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.role == UserRole.ADMIN or request.user.is_staff or request.user.is_superuser)
        )


class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.role in [UserRole.AUTHOR, UserRole.ADMIN] or request.user.is_staff)
        )


class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated
        )


class IsOwnerAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_user:
            return True
        if hasattr(obj, 'author'):
            if hasattr(obj.author, 'user') and obj.author.user:
                return obj.author.user == request.user
            return obj.author.email == request.user.email
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsOwnerMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_user:
            return True
        if hasattr(obj, 'member'):
            if hasattr(obj.member, 'user') and obj.member.user:
                return obj.member.user == request.user
            return obj.member.email == request.user.email
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False
