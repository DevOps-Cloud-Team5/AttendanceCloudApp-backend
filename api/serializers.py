from django.contrib.auth import get_user_model

from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator

from .models import AccountRoles, Course, CourseLecture, LectureTypes

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
        
class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLecture
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
        c = Course.objects.create(course_name=validated_data['course_name'])
        c.save()
        return c

class MassEnrollSerializer(serializers.Serializer):
    usernames = serializers.ListField(required=True, allow_empty=False, child=serializers.CharField(max_length=150))

    def validate_enroll(self, username):
        user_query = User.objects.all().filter(username=username)
        if not user_query: raise serializers.ValidationError({"error": f"user '{username}' does not exist"})
        if user_query[0].role == AccountRoles.ADMIN: raise serializers.ValidationError({"error": f"cannot enroll an admin account into a course"})
        
        course : Course = self.context.get("course")
        if course.is_user_enrolled(user_query[0]): raise serializers.ValidationError({"error": f"user '{username}' is already enrolled in '{course.course_name}'"})

    def validate(self, attrs):
        for username in attrs["usernames"]: self.validate_enroll(username)
        return attrs
    
class AddLectureSerializer(serializers.Serializer):
    MINIMUM_LECTURE_LENGTH = 10 # Minimum lecture length of 10 minutes
    
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)
    lecture_type = serializers.CharField(required=True)

    def validate(self, attrs):
        start_time, end_time = attrs["start_time"], attrs["end_time"]
        
        if start_time > end_time:
            raise serializers.ValidationError({"error": f"end_time has to be after start_time"})
        
        lecture_length = (end_time - start_time).seconds / 60
        if lecture_length < self.MINIMUM_LECTURE_LENGTH:
            raise serializers.ValidationError({"error": f"lecture has to be at least {self.MINIMUM_LECTURE_LENGTH} minutes"})
            
        lecture_type = attrs["lecture_type"]
        if lecture_type not in LectureTypes.values: 
            raise serializers.ValidationError({"error": f"invalid lecture type: '{lecture_type}'"})
        
        course : Course = self.context.get("course")
        for lecture in course.get_lectures():
            if lecture.start_time <= start_time and start_time < lecture.end_time:
                raise serializers.ValidationError({"error": "there is already an active lecture during this time range"})
            if lecture.start_time < end_time and end_time <= lecture.end_time:
                raise serializers.ValidationError({"error": "there is already an active lecture during this time range"})
        return attrs
    
class SetAttendenceTeacherSerializer(serializers.Serializer):
    usernames = serializers.DictField(required=True, allow_empty=False, child=
                                        serializers.CharField(max_length=150)
                                      )

    def validate_attendence(self, username, attended):
        user_query = User.objects.all().filter(username=username)
        if (attended := attended.lower()) not in ["true", "false"]: raise serializers.ValidationError({"error": f"invalid attendence state: '{attended}'"})
        if not user_query: raise serializers.ValidationError({"error": f"user '{username}' does not exist"})
        if user_query[0].role != AccountRoles.STUDENT: raise serializers.ValidationError({"error": f"cannot set the attendence of a non-student: '{username}' is {user_query[0].role}"})
        
        course : Course = self.context.get("course")
        if not course.is_user_enrolled(user_query[0]): raise serializers.ValidationError({"error": f"user '{username}' is not enrolled in '{course.course_name}'"})

    def validate(self, attrs):
        for username, attended in attrs["usernames"].items(): self.validate_attendence(username, attended)
        return attrs