from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser


# Create your models here.

class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=64, unique=True)
    user_name = models.CharField(max_length=64)
    password = models.CharField(max_length=256)
    is_admin = models.BooleanField(default=False)
    salt = models.CharField(max_length=64, null=True)

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "User"
        managed = True
