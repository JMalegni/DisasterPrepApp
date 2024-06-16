from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Users(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    location = models.CharField(max_length=50, default='Unknown')
    family_size = models.PositiveIntegerField(default = 1)
    medical_issues = models.TextField(blank=True, null=True)
    medication_amount = models.IntegerField(default=0)