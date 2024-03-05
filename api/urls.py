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

from .views import (
                    ping, 
                    genAdmin, 
                    
                    GetTokenView, 
                    
                    CreateUserView, 
                    UpdateUserView, 
                    DestroyUserView,
                    GetUserByUsername, 
                    GetUsersByRole, 
                    
                    CreateCourseView, 
                    UpdateCourseView, 
                    DestroyCourseView, 
                    EnrollCourseView,
                    GetCourseByName, 
                    GetCoursesAll, 
                    )

urlpatterns = [
    path('ping', ping),
    path('genadmin', genAdmin),
    
    # Manage tokens, by requesting one with credentials, refreshing or verifying one. Essentially the login API
    path('token/', GetTokenView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # All user paths
    path('user/register/', CreateUserView.as_view(), name='user_register'),
    path('user/update/<username>', UpdateUserView.as_view(), name='user_update'),
    path('user/delete/<username>', DestroyUserView.as_view(), name='user_delete'),
    path('user/get/<username>', GetUserByUsername.as_view(), name='user_get'),
    path('user/getrole/<role>', GetUsersByRole.as_view(), name='user_getrole'),
    
    # All course paths
    path('course/create/', CreateCourseView.as_view(), name='course_create'),
    path('course/update/<course_id>', UpdateCourseView.as_view(), name='course_update'),
    path('course/delete/<course_id>', DestroyCourseView.as_view(), name='course_delete'),
    path('course/enroll/<course_id>', EnrollCourseView.as_view(), name='course_enroll'),
    path('course/get/', GetCourseByName.as_view(), name='course_get'),
    path('course/getall/', GetCoursesAll.as_view(), name='course_getall'),
]