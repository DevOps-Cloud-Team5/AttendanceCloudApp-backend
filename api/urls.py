"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import test, test_auth, RegisterView, CustomTokenView, GetUser, GetUsersByRole

urlpatterns = [
    path('test', test),
    path('testauth', test_auth.as_view()),
    
    # Manage tokens, by requesting one with credentials, refreshing or verifying one.
    path('token/', CustomTokenView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Register new user
    path('user/register/', RegisterView.as_view(), name='auth_register'),
    path('user/get/<username>', GetUser.as_view(), name='auth_getuser'),
    path('users/get/<role>', GetUsersByRole.as_view(), name='auth_getusers'),
    
]