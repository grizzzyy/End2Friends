from django.db import models
from django.contrib.auth.models import AbstractUser

# Extending Django's built‑in AbstractUser so we keep all the default fields
# (username, email, password, date_joined, is_active, etc.)
# and then add the extra ones our app needs.

# Represents a user account, the thing that logs in
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
        
# What User Profile Represents the user profile, the thing that others see
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="profiles/", blank=True, null=True)
    display_name = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.display_name or self.user.username

 # Note: the User is about auth, perms, login creds, email, pass, amd username
 # Note: UserProfile is about how the user presents themselves, what others see on their page, dashboard data, preferences, settings, stats
 
 # Why have a separate UserProfile if we have extended AbstractUser?
 # Becuase the User model should stay focused on authentication and the UserProfile should handle everything else/