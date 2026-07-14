from django.contrib import admin
from .models import Reminder


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display  = ["company", "message", "user", "date", "remind_time", "done", "email_sent"]
    list_filter   = ["done", "email_sent", "date"]
    search_fields = ["company", "message", "user__email"]
    ordering      = ["date", "remind_time"]
