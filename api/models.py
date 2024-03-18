import datetime
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, UserManager
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator

# class User(AbstractUser):
#     class AccountRoles(models.TextChoices):
#         STUDENT = "student"
#         TEACHER = "teacher"
#         ADMIN = "admin"

#     role = models.CharField(
#         max_length=7,
#         choices=AccountRoles,
#         default=AccountRoles.STUDENT,
#     )
class AccountRoles(models.TextChoices):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class User(AbstractBaseUser):

    username = models.CharField(
        ("username"),
        max_length=150,
        unique=True,
        help_text=("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[UnicodeUsernameValidator()],
        error_messages={"unique": ("A user with that username already exists.")},
    )
    first_name = models.CharField(("first name"), max_length=150, blank=True)
    last_name = models.CharField(("last name"), max_length=150, blank=True)
    email = models.EmailField(("email address"), blank=True)
    force_pw_change = models.BooleanField(default=False)

    role = models.CharField(
        # max_length=1,
        choices=AccountRoles.choices,
        default=AccountRoles.STUDENT,
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_enrolled_courses(self):
        return [uc.course for uc in UserCourse.objects.filter(user__id=self.id)]

class LectureTypes(models.TextChoices):
    LECTURE = "lecture"
    PRACTICAL = "practical"
    WORKSHOP = "workshop"
    EXAM = "exam"
    
class Course(models.Model):
    course_name = models.CharField(max_length=50)

    objects = models.Manager()

    def __str__(self):
        return str(self.name)
    
    def get_enrolled_students(self):
        return [uc.user for uc in UserCourse.objects.filter(user__role=AccountRoles.STUDENT, course=self)]

    def get_teachers(self):
        return [uc.user for uc in UserCourse.objects.filter(user__role=AccountRoles.TEACHER, course=self)]

    def get_lectures(self):
        return CourseLecture.objects.filter(course=self)

    def get_lectures_week(self, year : int, week : int):
        return CourseLecture.objects.filter(course=self, start_time__year=year, start_time__week=week)

    def is_user_enrolled(self, user : User):
        return bool(UserCourse.objects.filter(user=user, course=self))

    def add_user_to_course(self, user: User):
        UserCourse.objects.create(user=user, course=self).save()

    def add_lecture_to_course(self, start_time: datetime.datetime, end_time: datetime.datetime, lecture_type : LectureTypes = LectureTypes.LECTURE):
        CourseLecture.objects.create(start_time=start_time, end_time=end_time, lecture_type=lecture_type, course=self).save()

# This is for storing users (teachers/students) in courses
class UserCourse(models.Model):
    user = models.ForeignKey(User, null=False, related_name='user', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, null=False, related_name='course', on_delete=models.CASCADE)

class CourseLecture(models.Model):
    course = models.ForeignKey(Course, null=False, related_name='course_lecture', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    lecture_type = models.CharField(
        choices=LectureTypes.choices,
        default=LectureTypes.LECTURE,
    )

    def set_attendence_user(self, student : User, attended : bool, teacher=False):
        queryset = AttendenceAcknowledgement.objects.filter(lecture=self, student=student)
        if not queryset: ack = AttendenceAcknowledgement.objects.create(lecture=self, student=student)
        else: ack = queryset[0]

        if teacher: ack.attended_teacher = attended
        else: ack.attended_student = attended
        ack.save()

    def get_attendence_user(self, student : User):
        queryset = AttendenceAcknowledgement.objects.filter(lecture=self, student=student)
        return None if not queryset else queryset[0]
    
    def get_attendence(self): 
        queryset = AttendenceAcknowledgement.objects.filter(lecture=self)
        return [] if not queryset else queryset[0]

class AttendenceAcknowledgement(models.Model):
    attended_student = models.BooleanField(default=None, null=True)
    attended_teacher = models.BooleanField(default=None, null=True)
    student = models.ForeignKey(User, null=False, related_name='user_ack', on_delete=models.CASCADE)
    lecture = models.ForeignKey(CourseLecture, null=False, related_name='lecture_ack', on_delete=models.CASCADE)



