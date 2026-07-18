from django.apps import AppConfig


class Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"

    def ready(self):
        # Fix "Network is unreachable" (Errno 101) SMTP errors on some cloud
        # hosts (like Render), which happens when Python resolves the mail
        # server's IPv6 address first but the host has no IPv6 egress route.
        # Force DNS resolution to IPv4-only, which avoids the broken path.
        import socket

        _original_getaddrinfo = socket.getaddrinfo

        def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

        socket.getaddrinfo = _ipv4_only_getaddrinfo
