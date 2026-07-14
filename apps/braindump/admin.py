from django.contrib import admin
from .models import BrainDump


@admin.register(BrainDump)
class BrainDumpAdmin(admin.ModelAdmin):
    list_display  = ["company", "role", "user", "date"]
    list_filter   = ["date"]
    search_fields = ["company", "role", "user__email"]
    ordering      = ["-created_at"]
