# jts_project/urls.py

from django.contrib import admin
from django.urls    import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import (
    RegisterView, LoginView, GoogleLoginView, UserProfileView,
    ForgotPasswordView, ResetPasswordView, ChangePasswordView,
    UserActivityView, RecordAccessView, HeartbeatView,
    ChangeEmailView, DeleteAccountView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # ─── Auth ────────────────────────────────────────────────────────────────
    path("api/auth/register/",        RegisterView.as_view(),       name="register"),
    path("api/auth/login/",           LoginView.as_view(),          name="login"),
    path("api/auth/token/refresh/",   TokenRefreshView.as_view(),   name="token_refresh"),
    path("api/auth/google/",          GoogleLoginView.as_view(),    name="google_login"),
    path("api/auth/me/",              UserProfileView.as_view(),    name="user_profile"),

    # ─── Password Reset ───────────────────────────────────────────────────────
    path("api/auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("api/auth/reset-password/",  ResetPasswordView.as_view(),  name="reset_password"),
    path("api/auth/change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("api/auth/change-email/",    ChangeEmailView.as_view(),    name="change_email"),
    path("api/auth/delete-account/",  DeleteAccountView.as_view(),  name="delete_account"),

    # ─── Activity Tracking ────────────────────────────────────────────────────
    path("api/auth/activity/",        UserActivityView.as_view(),   name="user_activity"),
    path("api/auth/record-access/",   RecordAccessView.as_view(),   name="record_access"),
    path("api/auth/heartbeat/",       HeartbeatView.as_view(),      name="heartbeat"),

    # ─── App endpoints ────────────────────────────────────────────────────────
    path("api/", include("apps.applications.urls")),
    path("api/", include("apps.reminders.urls")),
    path("api/", include("apps.braindump.urls")),

    # Allauth (Google OAuth flow)
    path("accounts/", include("allauth.urls")),
]
