from django.db import models

# Create your models here.

class Users(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    location = models.CharField(max_length=255, default='Unknown')
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    family_size = models.PositiveIntegerField(default = 1)
    medical_issues = models.TextField(blank=True, null=True)
    medication_amount = models.IntegerField(default=0)
    women_bool = models.BooleanField(default=False)
    child_bool = models.BooleanField(default=False)
    baby_bool = models.BooleanField(default=False)