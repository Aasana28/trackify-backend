# apps/applications/urls.py

from django.urls import path
from .views import ApplicationListCreateView, ApplicationDetailView, AddTimelineEntryView

urlpatterns = [
    path("applications/",         ApplicationListCreateView.as_view(), name="applications"),
    path("applications/<int:pk>/", ApplicationDetailView.as_view(),    name="application-detail"),
    path("applications/<int:pk>/timeline/", AddTimelineEntryView.as_view(), name="add-timeline"),
]
