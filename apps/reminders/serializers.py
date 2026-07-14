# apps/reminders/serializers.py

from rest_framework import serializers
from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Reminder
        fields = [
            "id", "application", "company", "message",
            "date", "remind_time", "done", "email_sent", "created_at"
        ]

    def create(self, validated_data):
        return Reminder.objects.create(
            user=self.context["request"].user,
            **validated_data
        )
