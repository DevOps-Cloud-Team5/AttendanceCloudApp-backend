from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
import os, re

from rest_framework import generics, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenSerializer, RegisterSerializer


__ROOT__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test(request):
    return JsonResponse({"data": "test"})

# Acts as the "login" API, provide username and password to get the access and refresh token
class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer

# The register API, requires the fields outlined in the RegisterSerializer
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer