# apps/braindump/urls.py

from django.urls import path
from .views import BrainDumpListCreateView, BrainDumpDetailView, AIProxyView

urlpatterns = [
    path("braindumps/",          BrainDumpListCreateView.as_view(), name="braindumps"),
    path("braindumps/<int:pk>/", BrainDumpDetailView.as_view(),     name="braindump-detail"),

    # Secure AI proxy — Anthropic API key never leaves the server
    path("ai/chat/",             AIProxyView.as_view(),             name="ai-chat"),
]
