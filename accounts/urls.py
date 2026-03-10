from django.urls import path
from . import views
from .views import people_view

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("register/", views.register_view, name="register"),
    path("people/", people_view, name="people"),
    path("profile/", views.profile_view, name="profile"),
    path("messages/", views.messages_view, name="messages_page"),
    path("settings/", views.settings_view, name="settings_page"),
]