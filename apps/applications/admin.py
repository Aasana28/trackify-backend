from django.contrib import admin
from .models import Application, TimelineEntry


class TimelineEntryInline(admin.TabularInline):
    model = TimelineEntry
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display  = ["company", "role", "user", "status", "applied_date", "follow_up_date"]
    list_filter   = ["status", "applied_date"]
    search_fields = ["company", "role", "user__email", "location"]
    ordering      = ["-created_at"]
    inlines       = [TimelineEntryInline]


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    list_display  = ["application", "stage", "date"]
    list_filter   = ["stage", "date"]
    search_fields = ["application__company", "stage"]
