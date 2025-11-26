from django.contrib import admin
from .models import ResourceCategory, MockResource


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'access_level', 'created_at')
    list_filter = ('access_level', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(MockResource)
class MockResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sensitivity_level', 'owner', 'created_at')
    list_filter = ('category', 'sensitivity_level', 'created_at')
    search_fields = ('name', 'description', 'owner__email')
    raw_id_fields = ('owner',)
    ordering = ('-created_at',)
