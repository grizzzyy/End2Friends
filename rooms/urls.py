from django.urls import path
from . import views

urlpatterns = [
    path("room/<int:room_id>/chat/", views.room_chat, name="room_chat"),
    path('join/<str:code>/', views.join_by_code, name='join_by_code'),
]
