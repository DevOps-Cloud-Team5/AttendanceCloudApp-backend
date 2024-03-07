from django.contrib.auth import get_user_model

from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator

from .models import Course

User = get_user_model()

# What information is stored in the JWT access token
class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        return token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

# Defines the rules for registering a new user. Required fields, validation rules etc.
class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all(), message="Username is already in use")])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all(), message="Email is already registered")])

    class Meta:
        model = User
        fields = ['username', 'email', 'password', "first_name", "last_name", "role"]

    def validate(self, attrs):
        if attrs.get("role", "") not in ["admin", "teacher", "student", ""]:
            raise serializers.ValidationError({"role": f"{attrs['role']} is not a valid role"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data["role"]
        )

        user.set_password(validated_data['password'])
        user.save()
        return user
    
class CourseCreateSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Course.objects.all(), message="course name is already in use")])

    class Meta:
        model = Course
        fields = ['course_name']

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        course_id = validated_data.get("course_id", "") or "_".join(validated_data['course_name'].lower().split())
        c = Course.objects.create(course_name=validated_data['course_name'], course_id=course_id)
        c.save()
        return c