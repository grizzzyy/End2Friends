# chat/urls.py
from django.urls import path, include

from django.contrib import admin


from .import views

urlpatterns = [
    path("", views.index, name="index"),
    path('',include('user,urls')),
    path('', include('chat.urls')),
]