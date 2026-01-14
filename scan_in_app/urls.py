"""Defines URL patters for scan_in_app."""

from django.urls import path

from . import views

app_name = "scan_in_app"
urlpatterns = [
    # Home Page
    path("", views.index, name="index"),
    path("time-in/", views.timeIn, name="time-in"),
    path("attendance/", views.monthly_attendance, name="monthly_attendance"),
]
