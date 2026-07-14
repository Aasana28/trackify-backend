# apps/applications/models.py
# Database table for job applications

from django.db import models
from django.conf import settings

class Application(models.Model):
    STATUS_CHOICES = [
        ("Applied",             "Applied"),
        ("Interview Scheduled", "Interview Scheduled"),
        ("Offer Received",      "Offer Received"),
        ("Rejected",            "Rejected"),
    ]

    # Each application belongs to a user
    user         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    # Core fields
    company      = models.CharField(max_length=200)
    role         = models.CharField(max_length=200)
    location     = models.CharField(max_length=200, blank=True)
    salary       = models.CharField(max_length=100, blank=True)
    status       = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Applied")
    applied_date = models.DateField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    notes        = models.TextField(blank=True)
    link         = models.URLField(blank=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # Newest first

    def __str__(self):
        return f"{self.company} — {self.role} ({self.user.email})"


class TimelineEntry(models.Model):
    """
    Each application can have multiple timeline stages.
    e.g. Applied -> OA -> Interview -> Offer
    """
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="timeline"
    )
    stage = models.CharField(max_length=100)
    date  = models.DateField()
    note  = models.TextField(blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.application.company} — {self.stage}"
