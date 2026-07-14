from django.db import models
from django.conf import settings
from apps.applications.models import Application


class Reminder(models.Model):
    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    application    = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True, blank=True)
    company        = models.CharField(max_length=200, default="General")
    message        = models.TextField()
    date           = models.DateField()
    remind_time    = models.TimeField(null=True, blank=True)   
    done           = models.BooleanField(default=False)
    email_sent     = models.BooleanField(default=False)        
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "remind_time"]

    def __str__(self):
        return f"{self.company} — {self.message[:40]}"
