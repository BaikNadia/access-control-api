from rest_framework import serializers
from .models import ResourceCategory, MockResource


class ResourceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceCategory
        fields = ('id', 'name', 'description', 'access_level',
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class MockResourceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)

    class Meta:
        model = MockResource
        fields = ('id', 'name', 'description', 'category', 'category_name',
                 'sensitivity_level', 'owner', 'owner_email',
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')


class MockResourceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockResource
        fields = ('name', 'description', 'category', 'sensitivity_level')
