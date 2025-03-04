from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('verify/phone/', views.verify_phone, name='verify_phone'),
    path('resend/code/', views.resend_verification_code, name='resend_code'),
    path('check/username/', views.check_username, name='check_username'),
    path('check/phone/', views.check_phone, name='check_phone'),
    path('interests/', views.update_user_interests, name='update_user_interests'),
    path('pictures/', views.update_pictures, name='update_pictures'),
]  