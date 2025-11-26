from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    """Allow access only to authenticated users"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active


class IsModerator(permissions.BasePermission):
    """Allow access only to moderators"""

    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.is_active and
                request.user.is_moderator)


class IsAdministrator(permissions.BasePermission):
    """Allow access only to administrators"""

    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.is_active and
                request.user.is_administrator)


class IsModeratorOrAdmin(permissions.BasePermission):
    """Allow access to moderators and administrators"""

    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.is_active and
                (request.user.is_moderator or request.user.is_administrator))


class IsOwnerOrModeratorOrAdmin(permissions.BasePermission):
    """Allow access to object owner, moderators, and administrators"""

    def has_object_permission(self, request, view, obj):
        # For user objects
        if hasattr(obj, 'id'):
            return (obj.id == request.user.id or
                    request.user.is_moderator or
                    request.user.is_administrator)

        # For other objects with user foreign key
        if hasattr(obj, 'user'):
            return (obj.user.id == request.user.id or
                    request.user.is_moderator or
                    request.user.is_administrator)

        return False


class ReadOnlyOrModeratorOrAdmin(permissions.BasePermission):
    """Allow read access to all authenticated users, write to moderators+"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated and request.user.is_active
        return (request.user.is_authenticated and
                request.user.is_active and
                (request.user.is_moderator or request.user.is_administrator))
