from django.db import models
from django.contrib.auth.models import AbstractUser

# Extending Django's built‑in AbstractUser so we keep all the default fields
# (username, email, password, date_joined, is_active, etc.)
# and then add the extra ones our app needs.
class User(AbstractUser):
    # Optional nickname the user can choose
    nickname = models.CharField(max_length=50, blank=True, null=True)

    # Short bio/about‑me section
    bio = models.TextField(blank=True, null=True)

    # Optional profile picture (stored in MEDIA_ROOT/profiles/)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    # Whether the user wants a more private account
    privacy_mode = models.BooleanField(default=False)

    def __str__(self):
        return self.username
