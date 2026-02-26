from django.urls import path
from . import views

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("dm/<str:username>/", views.start_dm, name="start_dm"),
    path("<str:room_name>/", views.chat_room, name="chat_room"),
]