# apps/applications/serializers.py

from rest_framework import serializers
from .models import Application, TimelineEntry


class TimelineEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model  = TimelineEntry
        fields = ["id", "stage", "date", "note"]


class ApplicationSerializer(serializers.ModelSerializer):
    # Include timeline entries nested inside each application
    timeline = TimelineEntrySerializer(many=True, read_only=True)

    class Meta:
        model  = Application
        fields = [
            "id", "company", "role", "location", "salary",
            "status", "applied_date", "follow_up_date",
            "notes", "link", "timeline", "created_at"
        ]

    def create(self, validated_data):
        # Automatically attach logged-in user
        user = self.context["request"].user
        application = Application.objects.create(user=user, **validated_data)

        # Auto-create first timeline entry
        TimelineEntry.objects.create(
            application=application,
            stage="Applied",
            date=application.applied_date or __import__("datetime").date.today(),
            note="Application logged"
        )
        return application
