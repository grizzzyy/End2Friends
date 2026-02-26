from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_channels, name="list_channels"),
    path("create/", views.create_channel, name="create_channel"),
    path("join/<int:channel_id>/", views.join_channel, name="join_channel"),
    path("leave/<int:channel_id>/", views.leave_channel, name="leave_channel"),
]