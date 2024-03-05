from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class AccountRoles(models.TextChoices):
        STUDENT = "student"
        TEACHER = "teacher"
        ADMIN = "admin"

    role = models.CharField(
        max_length=7,
        choices=AccountRoles,
        default=AccountRoles.STUDENT,
    )
    
class Course(models.Model):
    course_name = models.CharField(max_length=50)
    schedule = models.JSONField(default=list) 
    enrolled_students = models.JSONField(default=list)
    teachers = models.JSONField(default=list)

    objects = models.Manager()

    def __str__(self):
        return str(self.name)
