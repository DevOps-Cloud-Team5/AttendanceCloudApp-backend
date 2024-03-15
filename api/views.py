import datetime
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
from .models import Course, AccountRoles, CourseLecture
from .serializers import AddLectureSerializer, CustomTokenSerializer, CreateUserSerializer, LectureSerializer, MassEnrollSerializer, SetAttendenceTeacherSerializer, UserSerializer, CourseCreateSerializer, CourseSerializer

import pdb


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
    # pdb.set_trace()
    admins = UserSerializer(queryset.filter(role= AccountRoles.ADMIN), many=True)
    default_admin = UserSerializer(queryset.filter(username="admin"), many=True)
    if len(admins.data) + len(default_admin.data) != 0:
        return JsonResponse({"error": "admin account already setup"}, status=status.HTTP_403_FORBIDDEN)
    
    user = User.objects.create(
        username='admin',
        role=AccountRoles.ADMIN
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
        if not queryset:
            return Response({"error": f"user '{username}' not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset[0])
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
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class DestroyCourseView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class GetCourseByName(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, _, pk):
        queryset = self.get_queryset().filter(pk=pk)
        if not queryset:
            return Response({"error": f"course id '{pk}' not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset[0])
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetCoursesAll(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        if len(serializer.data) == 0:
            return Response({"error": "no courses found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            for course_serialized in serializer.data:
                course : Course = queryset.filter(pk=course_serialized["id"])[0]
                course_serialized["enrolled"] = course.is_user_enrolled(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

class EnrollCourseView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def post(self, request, *args, **kwargs):
        if request.user.role == AccountRoles.ADMIN: 
            return Response({"error": f"cannot enroll an admin account into a course"}, status=status.HTTP_400_BAD_REQUEST)
        
        obj : Course = self.get_object()
        user = request.user
        username = user.username
        
        if obj.is_user_enrolled(request.user):
            return Response({"error": f"{username} is already enrolled in {obj.course_name}"}, status=status.HTTP_400_BAD_REQUEST)
            
        obj.add_user_to_course(user)

        if getattr(obj, '_prefetched_objects_cache', None):
            obj._prefetched_objects_cache = {}
            
        return Response({"ok": f"succesfully enrolled {username} in {obj.course_name}"}, status=status.HTTP_200_OK)

class MassEnrollCourseView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    # Mass enroll students through admin accounts 
    def post(self, request, *args, **kwargs):
        course : Course = self.get_object()
        result = MassEnrollSerializer(data=request.data, context={ "course": course })
        result.is_valid(raise_exception=True)
        
        queryset = User.objects.all()
        usernames = result.data["usernames"]
        for username in usernames:
            user = queryset.filter(username=username)[0]
            course.add_user_to_course(user)
        
        return Response({"ok": f"succesfully enrolled {len(usernames)} students"}, status=status.HTTP_200_OK)

class GetCourseLecturesView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, _, *args, **kwargs):
        course : Course = self.get_object()
        lectures = course.get_lectures()   
        serializer = LectureSerializer(lectures, many=True)
        if len(serializer.data) == 0:
            return Response({"error": "no lectures found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

class AddLectureView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def post(self, request, *args, **kwargs):
        course : Course = self.get_object()
        result = AddLectureSerializer(data=request.data, context={ "course": course })
        result.is_valid(raise_exception=True)
        
        data = result.data
        start_time = datetime.datetime.fromisoformat(data["start_time"])
        end_time = datetime.datetime.fromisoformat(data["end_time"])
        course.add_lecture_to_course(start_time, end_time, data["lecture_type"])
        
        return Response({"ok": f"successfully created lecture"}, status=status.HTTP_200_OK)
    
class GetLectureView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = CourseLecture.objects.all()
    serializer_class = LectureSerializer

    def get(self, _, pk):
        queryset = self.get_queryset().filter(pk=pk)
        if not queryset:
            return Response({"error": f"course id '{pk}' not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset[0])
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SetStudentAttView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    lookup_field = 'pk'
    
    queryset = CourseLecture.objects.all()
    serializer_class = CourseLecture
    
    def post(self, request, *args, **kwargs):
        if request.user.role != AccountRoles.STUDENT:
            return Response({"error": f"cannot set the attendence of a non-student"}, status=status.HTTP_200_OK)
            
        lecture : CourseLecture = self.get_object()
        lecture.set_attendence_user(request.user, teacher=False)
        
        return Response({"ok": f"successfully set attendence"}, status=status.HTTP_200_OK)
    
class SetTeacherAttView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    lookup_field = 'pk'
    
    queryset = CourseLecture.objects.all()
    serializer_class = CourseLecture
    
    def post(self, request, *args, **kwargs):
        lecture : CourseLecture = self.get_object()
        result = SetAttendenceTeacherSerializer(data=request.data, context={ "course": lecture.course })
        result.is_valid(raise_exception=True)
        
        queryset = User.objects.all()
        usernames = result.data["usernames"]
        for username in usernames:
            user = queryset.filter(username=username)[0]
            lecture.set_attendence_user(user, teacher=True)
        
        return Response({"ok": f"succesfully set attendence for {len(usernames)} students"}, status=status.HTTP_200_OK)
    
class GetScheduleView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    def get(self, request, *args, **kwargs):
        user = User.objects.all().filter(username=request.user.username)[0]
        courses = user.get_enrolled_courses()
        all_lectures = []
        for course in courses:
            lectures_obj = course.get_lectures()
            lectures = LectureSerializer(lectures_obj, many=True)
            for i, lecture_obj in enumerate(lectures_obj):
                att = lecture_obj.get_attendence_user(user)
                lectures.data[i]["attended_student"] = att.attended_student if att is not None else False
                lectures.data[i]["attended_teacher"] = att.attended_teacher if att is not None else False
            all_lectures += lectures.data

        # Sort chronological order
        all_lectures.sort(key= lambda x : datetime.datetime.fromisoformat(x["start_time"]))

        return Response(all_lectures)