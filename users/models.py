from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)  
    weight = models.FloatField(null=True, blank=True)  
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    
    ACTIVITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]
    activity_level = models.CharField(max_length=10, choices=ACTIVITY_LEVELS, null=True, blank=True)

    email = models.EmailField(unique=True)

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']      

    def __str__(self):
        return self.username