from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    id = models.CharField(max_length=50, primary_key=True)
    businessPhones = models.CharField(max_length=15, null = True, blank=True)
    displayName = models.CharField(max_length=30, null = True, blank=True)
    jobTitle = models.CharField(max_length=20, null = True, blank=True)
    mobilePhone = models.CharField(max_length=15, null = True, blank=True)
    officeLocation = models.CharField(max_length=15, null = True, blank=True)
    # givenName = models.CharField(max_length=30, null = True, blank=True)