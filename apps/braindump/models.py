# apps/braindump/models.py

from django.db import models
from django.conf import settings
from apps.applications.models import Application

class BrainDump(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True, blank=True)
    company     = models.CharField(max_length=200)
    role        = models.CharField(max_length=200, blank=True)
    went_well   = models.TextField(blank=True)
    struggled   = models.TextField(blank=True)
    next_time   = models.TextField(blank=True)
    date        = models.DateField(auto_now_add=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"BrainDump — {self.company} ({self.user.email})"
