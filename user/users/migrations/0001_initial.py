# Generated by Django 5.1.6 on 2025-02-26 11:30

import django.contrib.auth.models
import django.utils.timezone
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('first_name', models.CharField(blank=True, max_length=50)),
                ('last_name', models.CharField(blank=True, max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, unique=True)),
                ('birth_date', models.DateField(default=django.utils.timezone.now)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile')),
                ('banner_picture', models.ImageField(blank=True, null=True, upload_to='banner')),
                ('interests', models.TextField(blank=True, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('count_followers', models.PositiveIntegerField(default=0)),
                ('count_following', models.PositiveIntegerField(default=0)),
                ('count_post', models.PositiveIntegerField(default=0)),
                ('is_private', models.BooleanField(default=False)),
                ('send_notifications', models.BooleanField(default=True)),
                ('allow_messages', models.BooleanField(default=True)),
                ('phone_verified', models.BooleanField(default=False)),
                ('verification_code', models.CharField(blank=True, max_length=6, null=True)),
                ('verification_code_created', models.DateTimeField(blank=True, null=True)),
                ('verification_attempts', models.IntegerField(default=0)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'db_table': 'users_customuser',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
