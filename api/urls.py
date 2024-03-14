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
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import (
                    AddLectureView,
                    GetCourseLecturesView,
                    GetLectureView,
                    MassEnrollCourseView,
                    test, 
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
    path('test', test),
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
    path('course/update/<pk>', UpdateCourseView.as_view(), name='course_update'),
    path('course/delete/<pk>', DestroyCourseView.as_view(), name='course_delete'),
    path('course/enroll/<pk>', EnrollCourseView.as_view(), name='course_enroll'),
    path('course/mass_enroll/<pk>', MassEnrollCourseView.as_view(), name='course_mass_enroll'),
    path('course/get/<pk>', GetCourseByName.as_view(), name='course_get'),
    path('course/getall/', GetCoursesAll.as_view(), name='course_getall'),
    
    path('course/lecture/<pk>/get', GetCourseLecturesView.as_view(), name='course_get_lecture'),
    path('course/lecture/<pk>/add', AddLectureView.as_view(), name='course_add_lecture'),
    # path('course/lecture/<pk>/update', GetCourseByName.as_view(), name='lecture_add'), # TODO
    # path('course/lecture/<pk>/delete', GetCourseByName.as_view(), name='lecture_add'),

    path('lecture/<pk>/get', GetLectureView.as_view(), name='lecture_get'),
    path('lecture/<pk>/student_att', GetLectureView.as_view(), name='lecture_get'),
    path('lecture/<pk>/teacher_att', GetLectureView.as_view(), name='lecture_get'),


    # Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional: Serve Swagger UI if you want a browsable API documentation
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]