from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class StudyChannel(models.Model):  # renamed
    room = models.ForeignKey(
        'rooms.StudyRoom',
        on_delete=models.CASCADE,
        related_name='channels',
        null =True,
        blank=True
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_channels")
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name

