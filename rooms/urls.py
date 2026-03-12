from django.urls import path
from . import views

app_name = "rooms"

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('create/', views.create_room, name='create_room'),

    # Room detail page (optional, but recommended)
    path('<int:room_id>/', views.room_detail, name='room_detail'),

    # Chat page
    path('<int:room_id>/chat/', views.room_chat, name='room_chat'),

    # Membership + invites
    path('<int:room_id>/join/', views.join_room, name='join_room'),
    path('<int:room_id>/invite/', views.send_invite, name='send_invite'),
    path('invites/', views.my_invites, name='my_invites'),
    path('invites/<int:invite_id>/accept/', views.accept_invite, name='accept_invite'),
    path('invites/<int:invite_id>/decline/', views.decline_invite, name='decline_invite'),
    path('join/<str:code>/', views.join_by_code, name='join_by_code'),
]
