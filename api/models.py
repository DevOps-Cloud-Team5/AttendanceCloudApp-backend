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