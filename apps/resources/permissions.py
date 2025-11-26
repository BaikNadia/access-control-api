from rest_framework import permissions


class ResourceAccessPermission(permissions.BasePermission):
    """
    Permission check based on resource sensitivity level and user role
    """

    def has_permission(self, request, view):
        # All authenticated users can access safe methods for basic resources
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated and request.user.is_active

        # Write operations require moderator+ role
        return (request.user.is_authenticated and
                request.user.is_active and
                (request.user.is_moderator or request.user.is_administrator))

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Administrators have full access
        if user.is_administrator:
            return True

        # Moderators can access up to level 3 resources
        if user.is_moderator:
            return obj.sensitivity_level <= 3

        # Regular users can only access their own resources up to level 2
        if hasattr(obj, 'owner'):
            return (obj.owner == user and obj.sensitivity_level <= 2)

        # For categories, regular users can only see up to internal level
        if hasattr(obj, 'access_level'):
            access_mapping = {
                'public': True,
                'internal': True,
                'confidential': user.is_moderator or user.is_administrator,
                'restricted': user.is_administrator
            }
            return access_mapping.get(obj.access_level, False)

        return False


class CanCreateResourcePermission(permissions.BasePermission):
    """Permission for creating resources"""

    def has_permission(self, request, view):
        if request.method == 'POST':
            return (request.user.is_authenticated and
                    request.user.is_active and
                    (request.user.is_moderator or request.user.is_administrator))
        return True


class HighSensitivityAccessPermission(permissions.BasePermission):
    """Access to high sensitivity resources (level 3-4)"""

    def has_object_permission(self, request, view, obj):
        user = request.user

        if obj.sensitivity_level >= 3:
            return user.is_moderator or user.is_administrator

        if obj.sensitivity_level == 4:
            return user.is_administrator

        return True
