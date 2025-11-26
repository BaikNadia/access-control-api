from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.db import transaction
from .models import User
from .serializers import (
    RegisterSerializer, LoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, UserAdminSerializer
)
from .permissions import (
    IsAuthenticated, IsOwnerOrModeratorOrAdmin, IsModeratorOrAdmin,
    IsAdministrator
)


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint
    No authentication required
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Auto-login after registration
        login(request, user)

        return Response({
            'message': 'User registered successfully',
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    User login endpoint with session authentication
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)

        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)

    return Response(
        {'error': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint
    """
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveAPIView):
    """
    Get current user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """
    Update current user profile
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'message': 'Profile updated successfully',
            'user': UserProfileSerializer(instance).data
        })


class UserDeleteView(generics.DestroyAPIView):
    """
    Soft delete user account (self-deletion)
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        # Logout user first
        logout(request)

        # Soft delete account
        user.soft_delete()

        return Response(
            {'message': 'User account deleted successfully'},
            status=status.HTTP_200_OK
        )


class UserListView(generics.ListAPIView):
    """
    List all users (moderators and admins only)
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserAdminSerializer
    permission_classes = [IsModeratorOrAdmin]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete user (moderators and admins only)
    """
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsOwnerOrModeratorOrAdmin]

    def perform_destroy(self, instance):
        """Soft delete instead of actual deletion"""
        instance.soft_delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'User account deactivated successfully'},
            status=status.HTTP_200_OK
        )


class UserRestoreView(generics.UpdateAPIView):
    """
    Restore soft-deleted user (admins only)
    """
    queryset = User.objects.filter(is_active=False)
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdministrator]

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        user.restore()

        return Response({
            'message': 'User account restored successfully',
            'user': UserAdminSerializer(user).data
        })
