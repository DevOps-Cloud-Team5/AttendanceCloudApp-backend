import os
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .permissions import IsTeacher, IsAdmin, IsStudent
from .models import Course
from .serializers import CustomTokenSerializer, CreateUserSerializer, UserSerializer, CourseCreateSerializer, CourseSerializer


User = get_user_model()
__ROOT__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@extend_schema(
    methods=['GET'],  # Specify methods if @api_view is not used, otherwise redundant
    summary="Ping Pong",
    description="Returns a simple ping to a pong response.",
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="Success - Returns a ping pong response."),
        # Add more status codes as needed
    }
)
@api_view(['GET'])
def test(request):
    return Response({"ping": "pong"}, 200)

# DEBUG function
# Generate an admin account if no admin accounts exists
# Dangerous endpoint which should be turned off in production but can be used to setup the DB
# Ideally a better method should be used to create the first admin account, but useful for debugging
def genAdmin(request):
    queryset = User.objects.all()
    admins = UserSerializer(queryset.filter(role="admin"), many=True)
    default_admin = UserSerializer(queryset.filter(username="admin"), many=True)
    if len(admins.data) + len(default_admin.data) != 0:
        return JsonResponse({"error": "admin account already setup"}, status=status.HTTP_403_FORBIDDEN)
    
    user = User.objects.create(
        username='admin',
        role='admin'
    )
    user.set_password('adminadmin')
    user.save()
    
    return JsonResponse({"ok": "admin account created"}, status=status.HTTP_200_OK)

# Acts as the "login" API, provide username and password to get the access and refresh token
class GetTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer

'''
User API reference

- Create user
- Update user
- Delete user
- Get user by username
- Get all users with a specific role
- Get all users in a specific course (TODO)

(Admins can do everything)
Create user can only be done by Admins
Update user can be done by the user itself, and by admins
Delete user can only be done by Admins
All GET requests should have authentication level of IsStudent
'''

# The register API, requires the fields outlined in the RegisterSerializer
class CreateUserView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

class UpdateUserView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class DestroyUserView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GetUserByUsername(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, _, username):
        queryset = self.get_queryset().filter(username=username)
        serializer = self.serializer_class(queryset, many=True)
        if len(serializer.data) == 0:
            return Response({"error": f"user '{username}' not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

class GetUsersByRole(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, _, role : str):
        role = role.lower()
        # if role == "admin" and not IsAdmin().has_permission(request): 
            # return Response({"error": "user is not permitted to view all admin accounts"}, status=status.HTTP_401_UNAUTHORIZED)
        
        queryset = self.get_queryset().filter(role=role)
        serializer = self.serializer_class(queryset, many=True)
        if len(serializer.data) == 0:
            return Response({"error": "no users found with that role"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

'''
Course API reference

- Create course
- Update course
- Delete course
- Enroll into course (has to be seperate from update)
- Get single course by name
- Get all courses

(Admins can do everything)
Create course can be done by Teachers
Update course can be done by Teachers
Delete course can be done by Teachers
All GET requests should have authentication level of IsStudent
'''

class CreateCourseView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    
    queryset = Course.objects.all()
    serializer_class = CourseCreateSerializer

class UpdateCourseView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    lookup_field = 'course_id'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class DestroyCourseView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    lookup_field = 'course_id'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class EnrollCourseView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    lookup_field = 'course_id'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def post(self, request, *args, **kwargs):
        req = request.data
        username = request.user.username
        if "username" not in req or req["username"] == "":
            return Response({"error", "username is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.role != "admin" and username != req["username"]:
            return Response({"error", "user does not have permissions for this action"}, status=status.HTTP_401_UNAUTHORIZED)
            
        obj = self.get_object()
        key, target_list = ("enrolled_students", obj.enrolled_students) if request.user.role == "student" else ("teachers", obj.teachers)
        
        if username in target_list:
            return Response({"error", f"user '{username}' is already part of '{obj.course_id}'"}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {key: target_list + [username]}
        serializer = self.get_serializer(obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(obj, '_prefetched_objects_cache', None):
            obj._prefetched_objects_cache = {}
        return Response(serializer.data)

class GetCourseByName(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, _, course_id):
        queryset = self.get_queryset().filter(course_id=course_id)
        serializer = self.serializer_class(queryset, many=True)
        if len(serializer.data) == 0:
            return Response({"error": f"course '{course_id}' not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

class GetCoursesAll(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, _):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        if len(serializer.data) == 0:
            return Response({"error": "no courses found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)
