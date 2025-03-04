from django.urls import path
from .views import list_interests

urlpatterns = [
    path('', list_interests, name='list_interests'),
] 