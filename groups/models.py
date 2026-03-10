from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class StudyChannel(models.Model):  # renamed
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_channels")
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("member", "Member"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(
        StudyChannel,  # <-- make sure this points to StudyChannel
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "channel")

    def __str__(self):
        return f"{self.user} -> {self.channel} ({self.role})"