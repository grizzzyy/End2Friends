from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Channel, PomodoroSession, Reminder, Activity, StudyRoom

User = get_user_model()

admin.site.register(User)
admin.site.register(Channel)
admin.site.register(PomodoroSession)
admin.site.register(Reminder)
admin.site.register(Activity)
admin.site.register(StudyRoom)