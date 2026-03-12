from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path("room/<int:room_id>/chat/", views.room_chat, name="room_chat"),
]
