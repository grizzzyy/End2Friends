from django.contrib import admin
from .models import StudyRoom, RoomMembership, RoomInvite
# the classrooms

@admin.register(StudyRoom)
class StudyRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "room_type", "is_private", "created_by", "created_at")
    list_filter = ("room_type", "is_private")
    search_fields = ("name", "description")


@admin.register(RoomMembership)
class RoomMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "role", "joined_at")
    list_filter = ("role",)
    search_fields = ("user__username", "room__name")


@admin.register(RoomInvite)
class RoomInviteAdmin(admin.ModelAdmin):
    list_display = ("room", "invited_user", "invited_by", "accepted", "created_at")
    list_filter = ("accepted",)
    search_fields = ("room__name", "invited_user__username", "invited_by__username")
