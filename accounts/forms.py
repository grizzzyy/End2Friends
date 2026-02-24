from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Task

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class CustomAuthenticationForm(AuthenticationForm):
    pass


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "due_date", "priority", "channel"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Task name", "class": "flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"}),
            "due_date": forms.DateInput(attrs={"type": "date", "class": "px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"}),
            "priority": forms.Select(attrs={"class": "px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"}),
            "channel": forms.TextInput(attrs={"placeholder": "#channel", "class": "px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"}),
        }

class ChannelForms(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ['name']
        widgets = {
        'name': forms.TextInput(attrs={
            'placeholder': 'channel-name',
            'class': 'border-purple-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400'
            })
        }