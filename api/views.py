from django.http import JsonResponse
from django.contrib.auth import get_user_model
import os

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenSerializer, RegisterSerializer, UserSerializer, CourseCreateSerializer, CourseSerializer

from rest_framework import generics, authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsTeacher, IsAdmin, IsStudent
from .models import Course

from rest_framework_simplejwt.authentication import JWTAuthentication
User = get_user_model()

__ROOT__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test(request):
    return JsonResponse({"data": str(request.user.is_authenticated)})

class test_auth(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return JsonResponse({"data": str(request.user.is_authenticated)})

class GetUser(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get(self, _, username):
        queryset = self.get_queryset().filter(username=username)
        serializer = self.serializer_class(queryset, many=True)
        if len(serializer.data) == 0:
            return Response({"error": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

class GetUsersByRole(generics.ListAPIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsStudent]
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'role'

    def get(self, request, role : str):
        role = role.lower()
        if role == "admin" and not IsAdmin().has_permission(request, None): 
            return Response({"error": "user is not permitted to view all admin accounts"}, status=status.HTTP_401_UNAUTHORIZED)
        
        queryset = self.get_queryset().filter(role=role.capitalize())
        serializer = self.serializer_class(queryset, many=True)
        if len(serializer.data) == 0:
            return Response({"error": "no users found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

class GetCourses(generics.ListAPIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsStudent]
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, _):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        if len(serializer.data) == 0:
            return Response({"error": "no courses found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

# Acts as the "login" API, provide username and password to get the access and refresh token
class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer

# The register API, requires the fields outlined in the RegisterSerializer
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    
class CourseCreateView(generics.CreateAPIView):
    queryset = Course.objects.all()
    permission_classes = (AllowAny,) # Should be only IsTeacher, but for debugging keep it at this
    serializer_class = CourseCreateSerializer