from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import ResourceCategory, MockResource
from .serializers import (
    ResourceCategorySerializer, MockResourceSerializer,
    MockResourceCreateSerializer
)
from .permissions import (
    ResourceAccessPermission, CanCreateResourcePermission,
)
from apps.users.permissions import IsAuthenticated, IsModeratorOrAdmin


class ResourceCategoryListView(generics.ListAPIView):
    """
    List resource categories with access control
    """
    queryset = ResourceCategory.objects.all()
    serializer_class = ResourceCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['access_level']
    search_fields = ['name', 'description']

    def get_queryset(self):
        user = self.request.user

        # Filter categories based on user role and access level
        if user.is_administrator:
            return ResourceCategory.objects.all()
        elif user.is_moderator:
            return ResourceCategory.objects.filter(
                Q(access_level='public') |
                Q(access_level='internal') |
                Q(access_level='confidential')
            )
        else:  # Regular user
            return ResourceCategory.objects.filter(
                Q(access_level='public') |
                Q(access_level='internal')
            )


class ResourceCategoryDetailView(generics.RetrieveAPIView):
    """
    Retrieve specific resource category
    """
    queryset = ResourceCategory.objects.all()
    serializer_class = ResourceCategorySerializer
    permission_classes = [IsAuthenticated, ResourceAccessPermission]


class MockResourceListView(generics.ListCreateAPIView):
    """
    List and create mock resources with access control
    """
    serializer_class = MockResourceSerializer
    permission_classes = [IsAuthenticated, CanCreateResourcePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'sensitivity_level']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'sensitivity_level', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        # Base queryset
        queryset = MockResource.objects.select_related('category', 'owner')

        # Filter based on user role
        if user.is_administrator:
            return queryset
        elif user.is_moderator:
            return queryset.filter(sensitivity_level__lte=3)
        else:  # Regular user
            # Users can see their own resources up to level 2, and public resources
            return queryset.filter(
                Q(owner=user, sensitivity_level__lte=2) |
                Q(sensitivity_level=1)  # Public resources
            )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MockResourceCreateSerializer
        return MockResourceSerializer

    def perform_create(self, serializer):
        # Set the owner to the current user
        serializer.save(owner=self.request.user)


class MockResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete mock resource
    """
    queryset = MockResource.objects.select_related('category', 'owner')
    serializer_class = MockResourceSerializer
    permission_classes = [IsAuthenticated, ResourceAccessPermission]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MockResourceCreateSerializer
        return MockResourceSerializer


class MyResourcesView(generics.ListAPIView):
    """
    List resources owned by current user
    """
    serializer_class = MockResourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'sensitivity_level']
    search_fields = ['name', 'description']

    def get_queryset(self):
        return MockResource.objects.filter(owner=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def access_test_view(request):
    """
    Test endpoint to verify access control based on user role
    """
    user = request.user
    user_data = {
        'email': user.email,
        'role': user.role,
        'permissions': []
    }

    # Test different access levels
    access_tests = {
        'public_access': True,  # All authenticated users
        'internal_access': True,  # All authenticated users
        'confidential_access': user.is_moderator or user.is_administrator,
        'restricted_access': user.is_administrator,
        'can_create_resources': user.is_moderator or user.is_administrator,
        'can_manage_users': user.is_moderator or user.is_administrator,
        'full_system_access': user.is_administrator
    }

    user_data['access_tests'] = access_tests
    user_data['effective_permissions'] = [key for key, value in access_tests.items() if value]

    return Response(user_data)


@api_view(['GET'])
@permission_classes([IsModeratorOrAdmin])
def admin_dashboard(request):
    """
    Admin dashboard - only accessible by moderators and admins
    """
    stats = {
        'total_users': MockResource.objects.count(),
        'total_categories': ResourceCategory.objects.count(),
        'total_resources': MockResource.objects.count(),
        'high_sensitivity_resources': MockResource.objects.filter(sensitivity_level__gte=3).count(),
        'recent_resources': MockResource.objects.order_by('-created_at')[:5].count()
    }

    return Response({
        'message': 'Welcome to Admin Dashboard',
        'stats': stats,
        'user': {
            'email': request.user.email,
            'role': request.user.role
        }
    })
