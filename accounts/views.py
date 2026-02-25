from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    TaskForm,
    ChannelForm,
    UpdateProfileForm,
    UpdateUserForm,
)

from .models import (
    Task,
    Channel,
    PomodoroSession,
    Reminder,
    Activity,
    StudyRoom,
)

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/accounts/dashboard/")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/accounts/dashboard/")
    else:
        form = CustomAuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    # Handle POST actions
    if request.method == "POST":

        # Add Task
        if "add_task" in request.POST:
            form = TaskForm(request.POST)
            channel_form = ChannelForm()  # keep other form available
            if form.is_valid():
                task = form.save(commit=False)
                task.user = request.user
                task.save()
                return redirect("dashboard")

        # Create Channel
        elif "create_channel" in request.POST:
            channel_form = ChannelForm(request.POST)
            form = TaskForm()  # keep other form available
            if channel_form.is_valid():
                channel = channel_form.save()
                channel.members.add(request.user)
                return redirect("dashboard")

    else:
        form = TaskForm()
        channel_form = ChannelForm()

    # Dashboard data
    tasks = Task.objects.filter(user=request.user, completed=False)[:5]
    channels = request.user.channels.all()[:5]
    pomodoro, _ = PomodoroSession.objects.get_or_create(user=request.user)
    reminders = Reminder.objects.filter(
        user=request.user,
        remind_at__gte=timezone.now()
    )[:5]
    activities = Activity.objects.filter(user=request.user)[:4]

    # Ensure correct related_name for StudyRoom
    study_rooms = (
        request.user.study_rooms.all()[:4]
        if hasattr(request.user, "study_rooms")
        else StudyRoom.objects.filter(members=request.user)[:4]
    )

    return render(
        request,
        "accounts/dashboard.html",
        {
            "tasks": tasks,
            "form": form,
            "channel_form": channel_form,
            "channels": channels,
            "pomodoro": pomodoro,
            "reminders": reminders,
            "activities": activities,
            "study_rooms": study_rooms,
        },
    )
  
@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(to='profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.userprofile)

    return render(request, 'accounts/profile.html', {'user_form': user_form, 'profile_form': profile_form})
