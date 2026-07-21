# apps/accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserActivity

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ["email", "name", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data["email"],
            email    = validated_data["email"],
            name     = validated_data.get("name", ""),
            password = validated_data["password"],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for returning user profile data"""
    class Meta:
        model  = User
        fields = ["id", "email", "name", "avatar_url", "created_at"]


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserActivity
        fields = ["date", "login_count", "access_count", "duration_seconds"]


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token       = serializers.UUIDField()
    new_password = serializers.CharField(min_length=6, write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    """For authenticated users changing their password from settings."""
    current_password = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(min_length=6, write_only=True)


class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    current_password = serializers.CharField(write_only=True)


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
