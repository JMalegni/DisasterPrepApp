from django.db import models

# Create your models here.

class Users(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    mobile = models.CharField(max_length=20)
