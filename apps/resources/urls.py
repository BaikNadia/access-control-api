from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    # Resource categories
    path('categories/', views.ResourceCategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.ResourceCategoryDetailView.as_view(), name='category-detail'),

    # Mock resources
    path('resources/', views.MockResourceListView.as_view(), name='resource-list'),
    path('resources/<int:pk>/', views.MockResourceDetailView.as_view(), name='resource-detail'),
    path('my-resources/', views.MyResourcesView.as_view(), name='my-resources'),

    # Test endpoints
    path('access-test/', views.access_test_view, name='access-test'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
]
