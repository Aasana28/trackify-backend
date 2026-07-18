# apps/applications/scheduler.py
# Checks for applications with no status update 3+ days after applying,
# and sends the user a follow-up reminder email.

import logging
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


def check_and_send_stale_application_alerts():
    """
    Find applications still marked 'Applied' where 3+ days have passed
    since the applied_date, and no alert has been sent yet.
    """
    from apps.accounts.email_utils import send_branded_email
    from .models import Application

    today = timezone.localtime(timezone.now()).date()
    cutoff = today - timedelta(days=3)

    stale = Application.objects.filter(
        status="Applied",
        applied_date__lte=cutoff,
        stale_alert_sent=False,
    ).select_related("user")

    for app in stale:
        user  = app.user
        email = user.email
        name  = user.name or email

        try:
            send_branded_email(
                subject=f"No update yet on your {app.company} application",
                to_email=email,
                heading=f"Hello {name},",
                body_lines=[
                    f"It's been 3 days since you applied to <b>{app.company}</b> "
                    f"for the role of <b>{app.role}</b>, and there's been no update yet.",
                    f"Applied on: {app.applied_date}<br>"
                    f"Location: {app.location or 'Not specified'}",
                    "Consider following up with the recruiter, or check for an update on the portal you applied through.",
                ],
                plain_text=(
                    f"Hello {name},\n\n"
                    f"It's been 3 days since you applied to {app.company} for the role of "
                    f"{app.role}, and there's been no update yet.\n\n"
                    f"Applied on: {app.applied_date}\n"
                    f"Location: {app.location or 'Not specified'}\n\n"
                    "Consider following up with the recruiter, or check for an update on the "
                    "portal you applied through.\n\n— Trackify Team"
                ),
                fail_silently=False,
            )
            app.stale_alert_sent = True
            app.save(update_fields=["stale_alert_sent"])
            logger.info(f"[StaleAlert] Sent email to {email} for application id={app.id}")
        except Exception as exc:
            logger.error(f"[StaleAlert] Failed to send email for id={app.id}: {exc}")
