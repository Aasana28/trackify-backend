# apps/reminders/scheduler.py
# Background scheduler that checks for due reminders and sends email notifications.
# Uses APScheduler (lightweight, no Redis needed). Runs inside the Django process.
#
# HOW IT WORKS:
#   - Every minute, check_and_send_reminders() runs.
#   - It queries Reminder rows where date+time <= now and email_sent=False.
#   - Sends an email to user.email and marks email_sent=True.

import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval     import IntervalTrigger
from django.utils                      import timezone

logger = logging.getLogger(__name__)

_scheduler = None


def check_and_send_reminders():
    """
    Query all pending (not-done, not-emailed) reminders whose scheduled
    datetime is in the past, and send email notifications.
    """
    # Import here to avoid circular import at module load time
    from apps.accounts.email_utils import send_branded_email
    from .models                   import Reminder

    now   = timezone.localtime(timezone.now())
    today = now.date()
    now_time = now.time().replace(second=0, microsecond=0)

    # Find reminders that should have been triggered by now
    due = Reminder.objects.filter(
        done=False,
        email_sent=False,
        date__lte=today,
    ).select_related("user")

    for reminder in due:
        # If reminder has a specific time, check it
        if reminder.remind_time:
            if reminder.date == today and reminder.remind_time > now_time:
                continue  # Not yet time
        
        # Send email
        user  = reminder.user
        email = user.email
        name  = user.name or email

        scheduled_str = str(reminder.date) + (
            f" at {reminder.remind_time.strftime('%H:%M')}" if reminder.remind_time else ""
        )

        try:
            send_branded_email(
                subject=f"Reminder: {reminder.company}",
                to_email=email,
                heading=f"Hello {name},",
                body_lines=[
                    "This is your scheduled reminder:",
                    f"<b>{reminder.message}</b>",
                    f"Company: {reminder.company}<br>Scheduled: {scheduled_str}",
                    "Log in to Trackify to mark it as done.",
                ],
                plain_text=(
                    f"Hello {name},\n\n"
                    f"This is your scheduled reminder:\n\n"
                    f"{reminder.message}\n\n"
                    f"Company: {reminder.company}\n"
                    f"Scheduled: {scheduled_str}"
                    + f"\n\nLog in to Trackify to mark it as done.\n\n— Trackify Team"
                ),
                fail_silently=False,
            )
            reminder.email_sent = True
            reminder.save(update_fields=["email_sent"])
            logger.info(f"[Reminder] Sent email to {email} for reminder id={reminder.id}")
        except Exception as exc:
            logger.error(f"[Reminder] Failed to send email for id={reminder.id}: {exc}")


def start_scheduler():
    """Start the background scheduler. Call once at app startup."""
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(timezone=str(timezone.get_current_timezone()))
    _scheduler.add_job(
        check_and_send_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="reminder_checker",
        replace_existing=True,
    )

    # Also check for stale (no-response) applications, once every hour
    from apps.applications.scheduler import check_and_send_stale_application_alerts
    _scheduler.add_job(
        check_and_send_stale_application_alerts,
        trigger=IntervalTrigger(hours=1),
        id="stale_application_checker",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("[Scheduler] Reminder scheduler started — checking every minute.")
