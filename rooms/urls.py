from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('create/', views.create_room, name='create_room'),
    path('<int:room_id>/', views.room_chat, name='room_chat'),
    path('<int:room_id>/join/', views.join_room, name='join_room'),
    path('<int:room_id>/invite/', views.send_invite, name='send_invite'),
    path('invites/', views.my_invites, name='my_invites'),
    path('invites/<int:invite_id>/accept/', views.accept_invite, name='accept_invite'),
    path('invites/<int:invite_id>/decline/', views.decline_invite, name='decline_invite'),
]