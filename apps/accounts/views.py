# apps/accounts/views.py
# Auth views: Register, Login, Google OAuth, Profile,
# Password Reset, Activity Tracking

from rest_framework              import status
from rest_framework.views        import APIView
from rest_framework.response     import Response
from rest_framework.permissions  import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth         import authenticate, get_user_model
from django.utils                import timezone
from django.conf                 import settings as django_settings
from datetime                    import timedelta
import requests

from .email_utils import send_branded_email
from .models      import PasswordResetToken, UserActivity
from .serializers import (
    RegisterSerializer, UserSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    ChangePasswordSerializer, UserActivitySerializer,
)

User = get_user_model()


# ─── Helpers ───────────────────────────────────────────────────────────────

def get_tokens_for_user(user):
    """Generate JWT access + refresh tokens for a user"""
    refresh = RefreshToken.for_user(user)
    return {
        "access":  str(refresh.access_token),
        "refresh": str(refresh),
    }


def record_login(user):
    """Increment today's login_count for a user."""
    today = timezone.localdate()
    obj, _ = UserActivity.objects.get_or_create(
        user=user, date=today,
        defaults={"login_count": 0, "access_count": 0}
    )
    obj.login_count  += 1
    obj.access_count += 1
    obj.save()


def record_access(user):
    """Increment today's access_count for a user (page visit/API call)."""
    today = timezone.localdate()
    obj, _ = UserActivity.objects.get_or_create(
        user=user, date=today,
        defaults={"login_count": 0, "access_count": 0}
    )
    obj.access_count += 1
    obj.save()


# Heartbeat interval used by the frontend (must match HEARTBEAT_INTERVAL_MS in usageTracker.js)
HEARTBEAT_INTERVAL_SECONDS = 30


def record_heartbeat(user):
    """
    Add one heartbeat's worth of active time to today's duration_seconds.
    Frontend pings this every HEARTBEAT_INTERVAL_SECONDS while the tab is open
    and visible, so this accumulates real "time spent in app" per day.
    """
    today = timezone.localdate()
    obj, _ = UserActivity.objects.get_or_create(
        user=user, date=today,
        defaults={"login_count": 0, "access_count": 0, "duration_seconds": 0}
    )
    obj.duration_seconds += HEARTBEAT_INTERVAL_SECONDS
    obj.save()


# ─── Auth Views ────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/auth/register/
    Body: { email, name, password }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user   = serializer.save()
            record_login(user)
            tokens = get_tokens_for_user(user)
            return Response({
                "user":    UserSerializer(user).data,
                "access":  tokens["access"],
                "refresh": tokens["refresh"],
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Body: { email, password }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email    = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        record_login(user)
        tokens = get_tokens_for_user(user)
        return Response({
            "user":    UserSerializer(user).data,
            "access":  tokens["access"],
            "refresh": tokens["refresh"],
        })


class GoogleLoginView(APIView):
    """
    POST /api/auth/google/
    Body: { access_token }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        google_token = request.data.get("access_token")
        if not google_token:
            return Response(
                {"error": "Google access token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        google_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {google_token}"}
        )

        if google_response.status_code != 200:
            return Response(
                {"error": "Invalid Google token."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        google_data = google_response.json()
        email      = google_data.get("email")
        name       = google_data.get("name", "")
        avatar_url = google_data.get("picture", "")

        if not email:
            return Response(
                {"error": "Could not get email from Google."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username":   email,
                "name":       name,
                "avatar_url": avatar_url,
            }
        )

        if not created:
            user.name       = name
            user.avatar_url = avatar_url
            user.save()

        record_login(user)
        tokens = get_tokens_for_user(user)
        return Response({
            "user":    UserSerializer(user).data,
            "access":  tokens["access"],
            "refresh": tokens["refresh"],
        })


class UserProfileView(APIView):
    """
    GET /api/auth/me/
    Also records a daily access event.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        record_access(request.user)
        return Response(UserSerializer(request.user).data)


# ─── Password Reset Views ──────────────────────────────────────────────────

class ForgotPasswordView(APIView):
    """
    POST /api/auth/forgot-password/
    Body: { email }
    Sends a password-reset link to the user's email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"].lower().strip()

        # Always return 200 to avoid email enumeration attacks
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "message": "If this email exists, a reset link has been sent."
            })

        # Invalidate old unused tokens
        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

        # Create new token (expires in 1 hour)
        token_obj = PasswordResetToken.objects.create(
            user       = user,
            expires_at = timezone.now() + timedelta(hours=1),
        )

        frontend_url = django_settings.FRONTEND_URL
        reset_link   = f"{frontend_url}/reset-password?token={token_obj.token}"

        name = user.name or user.email
        try:
            send_branded_email(
                subject="Password Reset Request",
                to_email=email,
                heading=f"Hello {name},",
                body_lines=[
                    "You requested to reset your Trackify password.",
                    "Click the button below to set a new one. This link is valid for 1 hour.",
                    "If you did not request this, you can safely ignore this email.",
                ],
                plain_text=(
                    f"Hello {name},\n\n"
                    f"You requested to reset your password.\n"
                    f"Click the link below (valid for 1 hour):\n\n"
                    f"{reset_link}\n\n"
                    f"If you did not request this, you can safely ignore this email.\n\n"
                    f"— Trackify Team"
                ),
                cta_text="Reset Password",
                cta_link=reset_link,
                fail_silently=True,
            )
        except Exception as e:
            # Log but still return success to avoid leaking info
            print(f"[Email Error] {e}")

        return Response({
            "message": "If this email exists, a reset link has been sent."
        })


class ResetPasswordView(APIView):
    """
    POST /api/auth/reset-password/
    Body: { token, new_password }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token_value  = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            token_obj = PasswordResetToken.objects.select_related("user").get(token=token_value)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not token_obj.is_valid():
            return Response(
                {"error": "This reset link has expired or already been used. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = token_obj.user
        user.set_password(new_password)
        user.save()

        token_obj.used = True
        token_obj.save()

        return Response({"message": "Password reset successfully. You can now log in."})


class ChangePasswordView(APIView):
    """
    POST /api/auth/change-password/
    For authenticated users (from Settings page).
    Body: { current_password, new_password }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        current_password = serializer.validated_data["current_password"]
        new_password     = serializer.validated_data["new_password"]

        if not request.user.check_password(current_password):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.set_password(new_password)
        request.user.save()

        # Send notification email
        name = request.user.name or request.user.email
        try:
            send_branded_email(
                subject="Password Changed",
                to_email=request.user.email,
                heading=f"Hello {name},",
                body_lines=[
                    "Your Trackify password was changed successfully.",
                    "If you did not make this change, please contact support immediately.",
                ],
                plain_text=(
                    f"Hello {name},\n\n"
                    f"Your Trackify password was changed successfully.\n"
                    f"If you did not do this, contact support immediately.\n\n"
                    f"— Trackify Team"
                ),
                fail_silently=True,
            )
        except Exception:
            pass

        return Response({"message": "Password changed successfully."})


# ─── Activity Tracking ─────────────────────────────────────────────────────

class UserActivityView(APIView):
    """
    GET /api/auth/activity/
    Returns today's and recent activity for the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()

        # Get or create today's record
        today_activity, _ = UserActivity.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={"login_count": 0, "access_count": 0}
        )

        # Last 7 days for history
        recent = UserActivity.objects.filter(
            user=request.user
        ).order_by("-date")[:7]

        return Response({
            "today": {
                "date":             str(today_activity.date),
                "login_count":      today_activity.login_count,
                "access_count":     today_activity.access_count,
                "duration_seconds": today_activity.duration_seconds,
            },
            "recent": UserActivitySerializer(recent, many=True).data,
        })


class RecordAccessView(APIView):
    """
    POST /api/auth/record-access/
    Called by frontend on page navigation to track access count.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        record_access(request.user)
        return Response({"status": "ok"})


class HeartbeatView(APIView):
    """
    POST /api/auth/heartbeat/
    Called by frontend every 30s while the app tab is open & visible.
    Adds 30s to today's duration_seconds for the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        record_heartbeat(request.user)
        return Response({"status": "ok"})
