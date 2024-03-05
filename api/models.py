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
    
class User(AbstractBaseUser):
    class AccountRoles(models.TextChoices):
        STUDENT = "student"
        TEACHER = "teacher"
        ADMIN = "admin"
    
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
    courses = models.JSONField(default=list, blank=True) 

    role = models.CharField(
        max_length=7,
        choices=AccountRoles,
        default=AccountRoles.STUDENT,
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
    
class Course(models.Model):
    course_id = models.CharField(max_length=50, primary_key=True)
    course_name = models.CharField(max_length=50)
    schedule = models.JSONField(default=list) 
    enrolled_students = models.JSONField(default=list)
    teachers = models.JSONField(default=list)

    objects = models.Manager()

    def __str__(self):
        return str(self.name)
