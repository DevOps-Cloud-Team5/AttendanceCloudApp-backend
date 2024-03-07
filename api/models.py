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
    STUDENT = "S", "Student"
    TEACHER = "T", "Teacher"
    ADMIN = "A", "Admin"

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
        max_length=1,
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

    def get_classes(self):
        return [uc.course for uc in UserCourse.objects.filter(user__id=self.id)]

    
class Course(models.Model):
    course_name = models.CharField(max_length=50)
    schedule = models.JSONField(default=list) 

    objects = models.Manager()

    def __str__(self):
        return str(self.name)
    
    def get_enrolled_students(self):
        return [uc.user for uc in UserCourse.objects.filter(user__role=AccountRoles.STUDENT)]

    def get_teachers(self):
        return [uc.user for uc in UserCourse.objects.filter(user__role=AccountRoles.TEACHER)]

    def add_user_to_course(self, user: User):
        UserCourse.objects.create(user=user, course=self)

# This is for storing users (teachers/students) in courses
class UserCourse(models.Model):
    user = models.ForeignKey(User, null=False, related_name='user', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, null=False, related_name='course', on_delete=models.CASCADE)

