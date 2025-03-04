from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'interests'
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
  
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False)  
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    phone_number = PhoneNumberField(unique=True)
    birth_date = models.DateField(default=timezone.now)
    profile_picture = models.ImageField(upload_to='profile', blank=True, null=True)
    banner_picture = models.ImageField(upload_to='banner', blank=True, null=True)
    interests = models.ManyToManyField(Interest, related_name='users', blank=True)
    bio = models.TextField(blank=True, null=True)
    count_followers = models.PositiveIntegerField(default=0)
    count_following = models.PositiveIntegerField(default=0)
    count_post = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)
    send_notifications = models.BooleanField(default=True)
    allow_messages = models.BooleanField(default=True)
    phone_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_created = models.DateTimeField(null=True, blank=True)
    verification_attempts = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users_customuser'

    def __str__(self):
        return self.username
