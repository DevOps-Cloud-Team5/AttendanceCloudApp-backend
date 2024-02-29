from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
import os, re

import rest_framework_simplejwt.serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny

__ROOT__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test(request):
    return JsonResponse({"data": "test"})

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class CustomTokenSerializer(serializers.TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('username', 'email', 'password', "first_name", "last_name")

    def validate(self, attrs):
        return attrs

    def create(self, data):
        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        user.set_password(data['password'])
        user.save()
        return user
