from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image

# Represents a user account, the thing that logs in
class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    privacy_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# UserProfile is about how the user presents themselves — what others see.
# User handles auth/credentials; UserProfile handles presentation, dashboard data, preferences, stats.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="profiles/", blank=True, null=True)
    display_name = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            img = Image.open(self.avatar.path)

        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)
    def __str__(self):
        return self.display_name or self.user.username


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    channel = models.CharField(max_length=100, blank=True, default='#reminders')
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date', '-priority']

    def __str__(self):
        return self.title


class Channel(models.Model):
    """Represents a chat channel that users can join."""
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='channels')
    unread_count = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_activity']

    def __str__(self):
        return f"#{self.name}"


class PomodoroSession(models.Model):
    """Tracks a user's Pomodoro timer session."""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('break', 'Break'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pomodoro')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    minutes_remaining = models.PositiveIntegerField(default=25)
    session_duration = models.PositiveIntegerField(default=25)
    break_duration = models.PositiveIntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Pomodoro"


class Reminder(models.Model):
    """Time-based reminders, events, and deadlines."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=200)
    remind_at = models.DateTimeField()
    channel = models.CharField(max_length=100, blank=True, default='#general')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['remind_at']

    def __str__(self):
        return self.title


class Activity(models.Model):
    """Recent activity feed items."""
    TYPE_CHOICES = [
        ('mention', 'Mention'),
        ('file', 'File Upload'),
        ('message', 'New Messages'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    channel = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.activity_type} in {self.channel}"


class StudyRoom(models.Model):
    """Private study rooms for collaboration."""
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='account_study_rooms')
    active_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='account_active_in_rooms', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def active_count(self):
        return self.active_members.count()