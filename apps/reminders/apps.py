# apps/reminders/apps.py

from django.apps import AppConfig


class RemindersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reminders"

    def ready(self):
        """
        Start the background reminder scheduler when Django boots.
        Guard against double-start in dev (reloader spawns two processes).
        """
        import os
        if os.environ.get("RUN_MAIN") != "true":
            # In production (gunicorn/uwsgi) RUN_MAIN is not set — always start.
            # In dev with --noreload, also always start.
            try:
                from .scheduler import start_scheduler
                start_scheduler()
            except Exception as e:
                print(f"[Reminders] Could not start scheduler: {e}")
        else:
            # This is the reloader child process — safe to start scheduler here
            try:
                from .scheduler import start_scheduler
                start_scheduler()
            except Exception as e:
                print(f"[Reminders] Could not start scheduler: {e}")
