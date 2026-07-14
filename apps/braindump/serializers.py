# apps/braindump/serializers.py

from rest_framework import serializers
from .models import BrainDump


class BrainDumpSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BrainDump
        fields = ["id", "application", "company", "role", "went_well", "struggled", "next_time", "date", "created_at"]
        read_only_fields = ["date", "created_at"]
