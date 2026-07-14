# apps/accounts/models.py
# Custom User model + Password Reset + Activity Tracking

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class User(AbstractUser):
    """
    Custom user model.
    We use email as the main login field instead of username.
    """
    email      = models.EmailField(unique=True)
    name       = models.CharField(max_length=150, blank=True)
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class PasswordResetToken(models.Model):
    """
    Secure time-limited password reset tokens.
    Each token is a UUID, expires after 1 hour, single-use.
    """
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_tokens")
    token      = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used       = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def is_valid(self):
        """Returns True if token has not been used and hasn't expired."""
        return not self.used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Reset token for {self.user.email}"


class UserActivity(models.Model):
    """
    Tracks daily login count and time spent (in seconds) per user.
    One record per user per day.
    """
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    date             = models.DateField()
    login_count      = models.PositiveIntegerField(default=0)
    access_count     = models.PositiveIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("user", "date")]
        ordering        = ["-date"]

    def __str__(self):
        return f"{self.user.email} — {self.date} — logins:{self.login_count} duration:{self.duration_seconds}s"
