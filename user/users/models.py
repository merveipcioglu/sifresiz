from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from .fields import EncryptedCharField, EncryptedTextField, PasswordField


class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'interests'
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    username = EncryptedCharField(max_length=255, hash_field='username_hash', unique=True)
    username_hash = models.CharField(max_length=64, db_index=True, unique=True)
    phone_number = EncryptedCharField(max_length=255, hash_field='phone_number_hash')
    phone_number_hash = models.CharField(max_length=64, db_index=True, null=True, blank=True)
    first_name = EncryptedCharField(max_length=255, blank=True)
    last_name = EncryptedCharField(max_length=255, blank=True)
    email = EncryptedCharField(max_length=255, blank=True)
    bio = EncryptedTextField(blank=True, null=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    profile_picture = models.ImageField(upload_to='profile', blank=True, null=True)
    banner_picture = models.ImageField(upload_to='banner', blank=True, null=True)
    interests = models.ManyToManyField(Interest, related_name='users', blank=True)
    count_followers = models.PositiveIntegerField(default=0)
    count_following = models.PositiveIntegerField(default=0)
    count_post = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)
    send_notifications = models.BooleanField(default=True)
    allow_messages = models.BooleanField(default=True)
    phone_verified = models.BooleanField(default=False)
    verification_code_created = models.DateTimeField(null=True, blank=True)
    verification_attempts = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.phone_number:
            from .encryption import generate_hash
            self.phone_number_hash = generate_hash(str(self.phone_number))
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            raise e

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users_customuser'

    def __str__(self):
        return self.username

    @classmethod
    def get_by_username(cls, username):
        from .encryption import generate_hash
        username_hash = generate_hash(username)
        return cls.objects.filter(username_hash=username_hash).first()

    @classmethod
    def get_by_phone(cls, phone):
        from .encryption import generate_hash
        phone_hash = generate_hash(phone)
        return cls.objects.filter(phone_number_hash=phone_hash).first()

