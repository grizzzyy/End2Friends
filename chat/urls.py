# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="chat_index"),
    path("<str:room_name>/", views.chat_room, name="chat_room"),
]
