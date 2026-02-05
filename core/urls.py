from django.urls import path
from .views import landing, dashboard

urlpatterns = [
    path("", landing, name="landing"),
    path("dashboard/", dashboard, name="dashboard"),
]
