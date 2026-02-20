from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, TaskForm
from .models import Task, Channel, PomodoroSession, Reminder, Activity, StudyRoom
from django.utils import timezone

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
    if request.method == "POST": # When form is submitted
        form = TaskForm(request.POST) # Get submitted data
        if form.is_valid():
            task = form.save(commit=False)# Create task but don't save yet
            task.user = request.user       # Assign to logged-in user
            task.save()                    # Now save to database
            return redirect("dashboard")   # Reload the page
    else:
        form = TaskForm()                  # Empty form for GET request
    
    tasks = Task.objects.filter(user=request.user, completed=False)[:5]
    channels = request.user.channels.all()[:5]
    pomodoro, _ = PomodoroSession.objects.get_or_create(user=request.user)
    reminders = Reminder.objects.filter(user=request.user, remind_at__gte=timezone.now())[:5]
    activities = Activity.objects.filter(user=request.user)[:4]
    study_rooms = request.user.study_rooms.all()[:4]
    return render(request, "accounts/dashboard.html", {"tasks": tasks, "form": form, "channels": channels, "pomodoro": pomodoro, "reminders": reminders, "activities": activities, "study_rooms": study_rooms})
