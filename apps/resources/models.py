from django.db import models
from django.conf import settings


class ResourceCategory(models.Model):
    """
    Mock resource category for access control testing
    """
    objects = None
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    access_level = models.CharField(
        max_length=20,
        choices=(
            ('public', 'Public'),
            ('internal', 'Internal'),
            ('confidential', 'Confidential'),
            ('restricted', 'Restricted'),
        ),
        default='internal'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resource_categories'
        verbose_name_plural = 'Resource categories'

    def __str__(self):
        return f"{self.name} ({self.access_level})"


class MockResource(models.Model):
    """
    Mock resource object for access control testing
    """
    objects = None
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE)

    # Resource sensitivity level
    sensitivity_level = models.IntegerField(
        choices=(
            (1, 'Level 1 - Public'),
            (2, 'Level 2 - Internal'),
            (3, 'Level 3 - Confidential'),
            (4, 'Level 4 - Restricted'),
        ),
        default=1
    )

    # Ownership for testing user-specific access
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_resources'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mock_resources'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (Level {self.sensitivity_level})"
