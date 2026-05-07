"""
URL configuration for RehabWeb_API project.
"""

from django.contrib import admin
from django.urls import path, include
from RehabWeb_API.views import LoginView, ProfileView, RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/auth/login/', LoginView.as_view(), name='api-login'),
    path('api/auth/register/', RegisterView.as_view(), name='api-register'),
    path('api/auth/profile/', ProfileView.as_view(), name='api-profile'),
]
