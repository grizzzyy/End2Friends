from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # Editing
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    # Deleting (soft delete)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Pinning / Flaggingx
    is_pinned = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-is_pinned", "-timestamp"]

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"