import datetime
import os
from typing import List
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
from .models import AttendenceAcknowledgement, Course, AccountRoles, CourseLecture

from .serializers import AddLectureSerializer, CourseUserSerializer, CustomTokenSerializer, CreateUserSerializer, LectureSerializer, MailTestSerializer, MassEnrollSerializer, SetAttendenceTeacherSerializer, UserSerializer, CourseCreateSerializer, CourseSerializer



from django.core.mail import send_mail


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
    """
    A simple API endpoint that responds with a 'pong' to a 'ping' request.
    
    Args:
        request (Request): The request object.
    
    Returns:
        Response: A JSON response containing {"ping": "pong"}.
    """
    return Response({"ping": "pong"}, 200)

@extend_schema(
    methods=['GET'],  # Specify methods if @api_view is not used, otherwise redundant
    summary="Ping Pong 2",
    description="Returns a simple ping to a pong2 response.",
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="Success - Returns a ping pong2 response."),
        # Add more status codes as needed
    }
)
@api_view(['GET'])
def test2(request):
    """
    A simple API endpoint that responds with a 'pong2' to a 'ping' request.
    
    Args:
        request (Request): The request object.
    
    Returns:
        Response: A JSON response containing {"ping": "pong2"}.
    """
    return Response({"ping": "pong2"}, 200)

@extend_schema(
    summary="Send Test Email",
    description="Tries to send a test email.",
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="Success - An email was sent."),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Failure - No email given as a parameter."),
        status.HTTP_418_IM_A_TEAPOT: OpenApiResponse(description="Failure - The email could not be sent.")
    }
)
class MailTestView(generics.CreateAPIView):
    """
    API endpoint that attempts to send a test email to the provided email address.
    Utilizes the MailTestSerializer for input validation.
    """
    serializer_class = MailTestSerializer

    def post(self, request, *args, **kwargs):
        """
        Sends a test email to the specified address.

        Args:
            request (Request): The request object, containing the 'email' field.

        Returns:
            Response: A JSON response indicating the success or failure of the email sending operation.
        """
        subject = 'Welcome to My Site'
        message = 'Thank you for creating an account!'
        from_email = 'admin@mysite.com'
        recipient_list = [request.POST.get("email", "")]
        if recipient_list[0] == "":
            Response({"status": "fail"}, 400)
        ret_code = send_mail(subject, message, from_email, recipient_list)
        if ret_code == 1:
            Response({"status": "success"}, 200)
        else:
            Response({"status": "fail", "return_code": ret_code}, 418)


# DEBUG function
# Generate an admin account if no admin accounts exists
# Dangerous endpoint which should be turned off in production but can be used to setup the DB
# Ideally a better method should be used to create the first admin account, but useful for debugging
def genAdmin(request):
    """
    Generates an admin account if no admin accounts exist. This is a debug function and
    should be disabled in production environments.

    Args:
        request (HttpRequest): The request object.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the admin account creation.
    """
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
    """
    API endpoint for obtaining JWT authentication tokens (access and refresh tokens).
    Utilizes CustomTokenSerializer for token generation.
    """
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
    """
    API endpoint for creating a new user account. Requires admin privileges.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

class UpdateUserView(generics.UpdateAPIView):
    """
    API endpoint for updating user details. Requires the user itself or an admin to perform the update.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class DestroyUserView(generics.DestroyAPIView):
    """
    API endpoint for deleting a user account. Requires admin privileges.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GetUserByUsername(generics.RetrieveAPIView):
    """
    Retrieves a user's details by their username. Accessible by students.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, _, username):
        """
        Fetches and returns the details of a user identified by username.

        Args:
            _ (HttpRequest): The request object.
            username (str): The username of the user to fetch.

        Returns:
            Response: A JSON response with the user's details or an error message.
        """
        queryset = self.get_queryset().filter(username=username)
        if not queryset:
            return Response({"error": f"user '{username}' not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset[0])
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetUsersByRole(generics.ListAPIView):
    """
    API endpoint to list users by their role. Accessible by students but primarily intended for administrative purposes.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, _, role : str):
        """
        Fetches and returns a list of users filtered by their role.

        Args:
            _ (HttpRequest): The request object.
            role (str): The role to filter users by.

        Returns:
            Response: A JSON response with a list of users matching the specified role or an error message.
        """
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
    """
    API endpoint for creating a new course. Accessible by teachers.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    
    queryset = Course.objects.all()
    serializer_class = CourseCreateSerializer

class UpdateCourseView(generics.UpdateAPIView):
    """
    API endpoint for updating existing course details. Accessible by teachers.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class DestroyCourseView(generics.DestroyAPIView):
    """
    API endpoint for deleting a course. Accessible by teachers.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class GetCourseByName(generics.RetrieveAPIView):
    """
    Retrieves course details by the course name. Accessible by students.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, _, pk):
        """
        Fetches and returns the details of a course identified by its primary key.

        Args:
            _ (HttpRequest): The request object.
            pk (str): The primary key of the course to fetch.

        Returns:
            Response: A JSON response with the course's details or an error message.
        """
        queryset = self.get_queryset().filter(pk=pk)
        if not queryset:
            return Response({"error": f"course id '{pk}' not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset[0])
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetFullCoursePage(generics.RetrieveAPIView):
    """
    Provides a detailed view of a course, including its lectures, attendance stats, enrolled students, and teachers. Accessible by students.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_attendence_stats(self, course, user):
        lectures : List[CourseLecture] = course.get_lectures()
        attendence_stats = {"attended": 0, "missed": 0}
        for lecture in lectures:
            if lecture.end_time > datetime.datetime.now(lecture.end_time.tzinfo): continue
            att = lecture.get_attendence_user(user)
            if att is None or not (att.attended_student and att.attended_teacher):
                attendence_stats["missed"] += 1
            else: attendence_stats["attended"] += 1
        return attendence_stats
    
    def get(self, request, pk):
        """
        Retrieves comprehensive information about a course, including lecture details and attendance statistics for the requesting user.

        Args:
            request (Request): The request object.
            pk (str): The primary key of the course to fetch.

        Returns:
            Response: A detailed JSON response including the course's info, attendance stats, and lists of enrolled students and teachers.
        """
        queryset = self.get_queryset().filter(pk=pk)
        if not queryset:
            return Response({"error": f"course id '{pk}' not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = User.objects.all().filter(username=request.user.username)[0]
        course : Course = queryset[0]
        teachers = course.get_teachers()
        students = course.get_enrolled_students()
        
        response_data = {}
        response_data["id"] = pk
        response_data["course_name"] = course.course_name
        response_data["num_teachers"] = len(teachers)
        response_data["num_students"] = len(students)
        response_data["enrolled"] = course.is_user_enrolled(user=user)
        response_data["attended"] = -1
        response_data["missed"] = -1
        response_data["users"] = CourseUserSerializer((teachers + students), many=True).data
    
        if user.role == AccountRoles.STUDENT: 
            response_data |= self.get_attendence_stats(course, user)
        
        return Response(response_data, status=status.HTTP_200_OK)

class GetCoursesAll(generics.ListAPIView):
    """
    Lists all courses. Accessible by students, includes information on enrollment and teacher/student numbers.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, request):
        """
        Fetches and returns a list of all courses, including enrollment status and number of teachers/students for each.

        Args:
            request (Request): The request object.

        Returns:
            Response: A JSON response with a list of all courses.
        """
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        if len(serializer.data) == 0:
            return Response({"error": "no courses found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            for course_serialized in serializer.data:
                course : Course = queryset.filter(pk=course_serialized["id"])[0]
                course_serialized["enrolled"] = course.is_user_enrolled(user=request.user)
                course_serialized["num_students"] = len(course.get_enrolled_students())
                course_serialized["num_teachers"] = len(course.get_teachers())
                
            return Response(serializer.data, status=status.HTTP_200_OK)

class EnrollCourseView(generics.GenericAPIView):
    """
    Enrolls a user into a specified course. If the username is provided and the requester is an admin, 
    it enrolls that user; otherwise, it enrolls the requester. Accessible by students and admins.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def post(self, request, username=None, *args, **kwargs):
        """
        Enrolls a user into a course based on the primary key provided in the URL.

        Args:
            request (Request): The request object.
            username (Optional[str]): The username of the user to enroll. Defaults to None.

        Returns:
            Response: A JSON response indicating the success or failure of the enrollment process.
        """
        if username is not None:
            if user.role != AccountRoles.ADMIN: 
                return Response({"error": f"unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
            queryset = User.objects.all().filter(username=username)
            if not queryset:
                return Response({"error": f"{username} is not a valid user"}, status=status.HTTP_400_BAD_REQUEST)
            user = queryset[0]
        else:
            user = request.user
            username = user.username
        
        if user.role == AccountRoles.ADMIN: 
            return Response({"error": f"cannot enroll an admin account into a course"}, status=status.HTTP_400_BAD_REQUEST)
        
        obj : Course = self.get_object()
        if obj.is_user_enrolled(user):
            return Response({"error": f"{username} is already enrolled in {obj.course_name}"}, status=status.HTTP_400_BAD_REQUEST)
            
        obj.add_user_to_course(user)

        if getattr(obj, '_prefetched_objects_cache', None):
            obj._prefetched_objects_cache = {}
            
        return Response({"ok": f"succesfully enrolled {username} in {obj.course_name}"}, status=status.HTTP_200_OK)

class DisenrollCourseView(generics.GenericAPIView):
    """
    Disenrolls a user from a specified course. If the username is provided and the requester is an admin, 
    it disenrolls that user; otherwise, it disenrolls the requester. Accessible by students and admins.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def post(self, request, username=None, *args, **kwargs):
        """
        Disenrolls a user from a course based on the primary key provided in the URL.

        Args:
            request (Request): The request object.
            username (Optional[str]): The username of the user to disenroll. Defaults to None.

        Returns:
            Response: A JSON response indicating the success or failure of the disenrollment process.
        """
        if username is not None:
            if request.user.role != AccountRoles.ADMIN: 
                return Response({"error": f"unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
            queryset = User.objects.all().filter(username=username)
            if not queryset:
                return Response({"error": f"{username} is not a valid user"}, status=status.HTTP_400_BAD_REQUEST)
            user = queryset[0]
        else:
            user = request.user
            username = user.username
        
        obj : Course = self.get_object()
        if not obj.is_user_enrolled(user):
            return Response({"error": f"{username} is not enrolled in {obj.course_name}"}, status=status.HTTP_400_BAD_REQUEST)
            
        obj.remove_user_from_course(user)

        if getattr(obj, '_prefetched_objects_cache', None):
            obj._prefetched_objects_cache = {}
            
        return Response({"ok": f"succesfully disenrolled {username} from {obj.course_name}"}, status=status.HTTP_200_OK)

class MassEnrollCourseView(generics.GenericAPIView):
    """
    Allows an admin to mass enroll multiple users into a specified course. Accessible by admins only.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    # Mass enroll students through admin accounts 
    def post(self, request, *args, **kwargs):
        """
        Enrolls multiple users into a course based on the primary key provided in the URL and 
        a list of usernames provided in the request body.

        Args:
            request (Request): The request object.

        Returns:
            Response: A JSON response indicating the success or failure of the mass enrollment process.
        """
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
    """
    Lists all lectures for a specified course. Accessible by students.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, _, *args, **kwargs):
        """
        Retrieves and returns all lectures for a course based on the primary key provided in the URL.

        Args:
            _ (HttpRequest): The request object.

        Returns:
            Response: A JSON response containing a list of lectures for the specified course.
        """
        course : Course = self.get_object()
        lectures = course.get_lectures()   
        serializer = LectureSerializer(lectures, many=True)
        if len(serializer.data) == 0:
            return Response({"error": "no lectures found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

class AddLectureView(generics.GenericAPIView):
    """
    Adds a single lecture or a series of lectures to a course. Accessible by teachers.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    lookup_field = 'pk'
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    holiday_weeks = [1, 8, 18, 29, 30, 31, 32, 33, 34, 42, 52]
    
    def post(self, request, *args, **kwargs):
        """
        Creates a new lecture or a series of lectures for a course based on the primary key provided in the URL 
        and the details provided in the request body.

        Args:
            request (Request): The request object.

        Returns:
            Response: A JSON response indicating the success or failure of the lecture(s) creation process.
        """
        course : Course = self.get_object()
        result = AddLectureSerializer(data=request.data, context={ "course": course })
        result.is_valid(raise_exception=True)
        
        data = result.data
        start_time = datetime.datetime.fromisoformat(data["start_time"])
        end_time = datetime.datetime.fromisoformat(data["end_time"])
        
        if not data["lecture_series"]:
            course.add_lecture_to_course(start_time, end_time, data["lecture_type"])
        else:
            curr_week = start_time.strftime("%W") 
            exclude_weeks = list(self.holiday_weeks)
            if curr_week in exclude_weeks: exclude_weeks.remove(curr_week)
            
            start_string = start_time.strftime("%Y %a %H %M %S ") 
            end_string = end_time.strftime("%Y %a %H %M %S ") 
            for i in range(1, 53):
                if i in exclude_weeks: continue
                new_start = datetime.datetime.strptime(start_string + str(i), "%Y %a %H %M %S %W")
                new_end = datetime.datetime.strptime(end_string + str(i), "%Y %a %H %M %S %W")
                course.add_lecture_to_course(new_start, new_end, data["lecture_type"])
                
        return Response({"ok": f"successfully created lecture"}, status=status.HTTP_200_OK)

class DestroyLectureView(generics.DestroyAPIView):
    """
    Deletes a lecture from a course. Accessible by teachers.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    lookup_field = 'pk'
    
    queryset = CourseLecture.objects.all()
    serializer_class = LectureSerializer

class GetLectureView(generics.RetrieveAPIView):
    """
    Retrieves details for a specific lecture. Accessible by students.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    queryset = CourseLecture.objects.all()
    serializer_class = LectureSerializer

    def get(self, _, pk):
        queryset = self.get_queryset().filter(pk=pk)
        if not queryset:
            return Response({"error": f"lecture id '{pk}' not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset[0])
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetFullLectureView(generics.RetrieveAPIView):
    """
    Provides detailed information about a specific lecture, including attendance data. 
    Accessible by teachers, this view includes details like the course name, list of students, 
    and their attendance status for the lecture.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    
    queryset = CourseLecture.objects.all()
    serializer_class = LectureSerializer

    def get(self, _, pk):
        """
        Fetches and returns detailed information for a lecture identified by its primary key,
        including the course name and student attendance.

        Args:
            _ (HttpRequest): The request object.
            pk (str): The primary key of the lecture to fetch.

        Returns:
            Response: A JSON response containing detailed lecture information.
        """
        queryset = self.get_queryset().filter(pk=pk)
        if not queryset:
            return Response({"error": f"lecture id '{pk}' not found"}, status=status.HTTP_404_NOT_FOUND)
        
        lecture : CourseLecture = queryset[0]
        course : Course = lecture.course
        
        serializer = self.serializer_class(lecture)
        response = dict(serializer.data)
        response["course_name"] = course.course_name
        response["students"] = []
        
        students = course.get_enrolled_students()
        for student in students:
            att : AttendenceAcknowledgement = lecture.get_attendence_user(student)
            attended = att.attended_teacher if att is not None else None
            data = {
                "first_name": student.first_name,
                "last_name": student.last_name,
                "username": student.username,
                "attended": attended
            }      
            response["students"].append(data)
        
        return Response(response, status=status.HTTP_200_OK)
    
def setAttendence(self, request, attended):
    """
    A helper function to set the attendance status of a student for a lecture. 
    This function is used internally by the SetStudentAttView and UnsetStudentAttView views.
    
    Args:
        request (Request): The request object.
        attended (bool): The attendance status to set for the student.

    Returns:
        Response: A JSON response indicating the success or failure of setting the attendance.
    """
    if request.user.role != AccountRoles.STUDENT:
        return Response({"error": f"cannot set the attendence of a non-student"}, status=status.HTTP_200_OK)
        
    lecture : CourseLecture = self.get_object()
    lecture.set_attendence_user(request.user, attended=attended, teacher=False)
    
    return Response({"ok": f"successfully set attendence"}, status=status.HTTP_200_OK)
    
class SetStudentAttView(generics.GenericAPIView):
    """
    Sets the attendance status of a student for a specific lecture to 'attended'. 
    Accessible by students, allowing them to mark themselves as having attended a lecture.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    lookup_field = 'pk'
    
    queryset = CourseLecture.objects.all()
    serializer_class = CourseLecture
    
    def post(self, request, *args, **kwargs):
        """
        Marks the requesting student as having attended the lecture specified by the primary key in the URL.

        Args:
            request (Request): The request object.

        Returns:
            Response: A JSON response indicating the success or failure of marking attendance.
        """
        return setAttendence(self, request, True)
        
class UnsetStudentAttView(generics.GenericAPIView):
    """
    Sets the attendance status of a student for a specific lecture to 'not attended'. 
    Accessible by students, allowing them to mark themselves as not having attended a lecture.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    lookup_field = 'pk'
    
    queryset = CourseLecture.objects.all()
    serializer_class = CourseLecture
    
    def post(self, request, *args, **kwargs):
        """
        Marks the requesting student as not having attended the lecture specified by the primary key in the URL.

        Args:
            request (Request): The request object.

        Returns:
            Response: A JSON response indicating the success or failure of marking non-attendance.
        """
        return setAttendence(self, request, False)
    
class SetTeacherAttView(generics.GenericAPIView):
    """
    Allows teachers to set the attendance status for students in a specific lecture. 
    This endpoint is intended for use by teachers to accurately record which students attended a lecture.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    lookup_field = 'pk'
    
    queryset = CourseLecture.objects.all()
    serializer_class = CourseLecture
    
    def post(self, request, *args, **kwargs):
        """
        Sets the attendance for multiple students in the lecture specified by the primary key in the URL,
        based on the data provided in the request body.

        Args:
            request (Request): The request object.

        Returns:
            Response: A JSON response indicating the success or failure of setting student attendance.
        """
        lecture : CourseLecture = self.get_object()
        result = SetAttendenceTeacherSerializer(data=request.data, context={ "course": lecture.course })
        result.is_valid(raise_exception=True)
        
        queryset = User.objects.all()
        usernames = result.data["usernames"]
        for username, attended in usernames.items():
            user = queryset.filter(username=username)[0]
            lecture.set_attendence_user(user, attended=(attended=="true"), teacher=True)
        
        return Response({"ok": f"succesfully set attendence for {len(usernames)} students"}, status=status.HTTP_200_OK)
    
    
class GetScheduleView(generics.GenericAPIView):
    """
    Retrieves the schedule of lectures for a student for a specified year and week. 
    Optionally, it can filter the schedule to include lectures for a specific course only. 
    Accessible by students, this endpoint helps them view their upcoming or past lecture schedule.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStudent]
    
    def get(self, request, year, week, course_id=None):
        """
        Fetches the lecture schedule for the requesting student for the given year and week. 
        If a course_id is provided, the schedule is limited to that course.

        Args:
            request (Request): The request object.
            year (str): The year for which to retrieve the schedule.
            week (str): The week number within the year for which to retrieve the schedule.
            course_id (Optional[str]): The ID of a specific course to filter the schedule. Defaults to None.

        Returns:
            Response: A JSON response containing the lecture schedule.
        """
        if not year.isdigit() or int(year) < 1970:
            return Response({"error": f"invalid year parameter"}, status=status.HTTP_400_BAD_REQUEST)
        if not week.isdigit() or int(week) < 0 or int(week) > 52:
            return Response({"error": f"invalid week parameter"}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.all().filter(username=request.user.username)[0]
        
        if course_id is None:
            courses : List[Course] = user.get_enrolled_courses()
        else: 
            queryset = Course.objects.all().filter(pk=course_id)
            if not queryset:
                return Response({"error": f"course ID is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            courses : List[Course] = [queryset[0]]
        
        all_lectures = []
        for course in courses: 
            lectures_obj = course.get_lectures_week(int(year), int(week))
            lectures = LectureSerializer(lectures_obj, many=True)
            for i, lecture_obj in enumerate(lectures_obj):
                att = lecture_obj.get_attendence_user(user)
                lectures.data[i]["course_name"] = lecture_obj.course.course_name
                lectures.data[i]["attended_student"] = att.attended_student if att is not None else None
                lectures.data[i]["attended_teacher"] = att.attended_teacher if att is not None else None
            all_lectures += lectures.data

        # Sort chronological order
        all_lectures.sort(key= lambda x : datetime.datetime.fromisoformat(x["start_time"]))

        return Response(all_lectures, status=status.HTTP_200_OK)
    
# @api_view(['GET'])
# def get_presigned_url(request):
#     s3_client = boto3.client('s3',
#                              aws_access_key_id = '',
#                              aws_secret_access_key='YOUR_AWS_SECRET_ACCESS_KEY',
#                              region_name='YOUR_AWS_REGION')

#     file_name = request.GET.get('file_name')
#     file_type = request.GET.get('file_type')

#     try:
#         presigned_post = s3_client.generate_presigned_post(
#             Bucket='YOUR_S3_BUCKET_NAME',
#             Key=file_name,
#             Fields={"acl": "public-read", "Content-Type": file_type},
#             Conditions=[
#               {"acl": "public-read"},
#               {"Content-Type": file_type}
#             ],
#             ExpiresIn=3600
#         )
#         return JsonResponse(presigned_post)
#     except NoCredentialsError:
#         return Response({"error": "Credentials are missing"}, status=403)