# apps/reminders/urls.py

from django.urls import path
from .views import ReminderListCreateView, ReminderDetailView, ToggleReminderView

urlpatterns = [
    path("reminders/",            ReminderListCreateView.as_view(), name="reminders"),
    path("reminders/<int:pk>/",   ReminderDetailView.as_view(),     name="reminder-detail"),
    path("reminders/<int:pk>/toggle/", ToggleReminderView.as_view(), name="toggle-reminder"),
]
