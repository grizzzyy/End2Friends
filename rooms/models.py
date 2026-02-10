from django.db import models
from django.conf import settings



class StudyRoom(models.Model):
    ROOM_TYPE = [
        ("study", "Study"),
        ("class", "Class"),
        ("group", "Group"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    room_type = models.CharField(
        max_length=10,
        choices=ROOM_TYPE
    )
    is_private = models.BooleanField(default=False)
    created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="study_rooms"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class RoomMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
    ]

    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="room_memberships"
)

    room = models.ForeignKey(
        "StudyRoom",
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="member"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} in {self.room} ({self.role})"

class RoomInvite(models.Model):
    room = models.ForeignKey(
        "StudyRoom",
        on_delete=models.CASCADE,
        related_name="invites"
    )
    invited_user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="room_invites"
)

    invited_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="sent_room_invites"
)

    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite to {self.room} for {self.invited_user}"
