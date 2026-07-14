# apps/accounts/email_utils.py
# Shared helper for sending branded transactional emails (HTML + plain text).
#
# WHY THIS EXISTS:
#   Plain send_mail() (text-only, emoji in subject, no HTML part) gets flagged
#   as spam far more often than a normal multipart email. This helper always
#   sends BOTH a plain-text part and an HTML part, uses a clean subject line,
#   and keeps a consistent from-name/from-address — all of which make the
#   email look like a normal transactional message instead of a bulk/script mail.

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def _build_html(heading: str, body_lines: list[str], cta_text: str | None = None, cta_link: str | None = None) -> str:
    """Build a simple, clean HTML email body. Inline CSS only (required for email clients)."""
    paragraphs = "".join(
        f'<p style="margin:0 0 14px 0;color:#374151;font-size:15px;line-height:1.6;">{line}</p>'
        for line in body_lines
    )

    cta_html = ""
    if cta_text and cta_link:
        cta_html = f"""
        <div style="text-align:center;margin:28px 0 10px 0;">
          <a href="{cta_link}"
             style="background-color:#4f46e5;color:#ffffff;text-decoration:none;
                    padding:12px 28px;border-radius:8px;font-size:15px;font-weight:600;
                    display:inline-block;">
            {cta_text}
          </a>
        </div>
        <p style="font-size:12px;color:#9ca3af;text-align:center;word-break:break-all;">
          Or copy this link: {cta_link}
        </p>
        """

    return f"""\
<!DOCTYPE html>
<html>
  <body style="margin:0;padding:0;background-color:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:32px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="480" cellpadding="0" cellspacing="0"
                 style="background-color:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e5e7eb;">
            <tr>
              <td style="background-color:#4f46e5;padding:22px 32px;">
                <span style="color:#ffffff;font-size:20px;font-weight:700;letter-spacing:0.3px;">Trackify</span>
              </td>
            </tr>
            <tr>
              <td style="padding:32px;">
                <h2 style="margin:0 0 16px 0;color:#111827;font-size:18px;">{heading}</h2>
                {paragraphs}
                {cta_html}
              </td>
            </tr>
            <tr>
              <td style="padding:18px 32px;background-color:#f9fafb;border-top:1px solid #e5e7eb;">
                <p style="margin:0;color:#9ca3af;font-size:12px;">
                  This is an automated message from Trackify. Please don't reply to this email.
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""


def send_branded_email(
    subject: str,
    to_email: str,
    heading: str,
    body_lines: list[str],
    plain_text: str,
    cta_text: str | None = None,
    cta_link: str | None = None,
    fail_silently: bool = False,
) -> bool:
    """
    Send a branded transactional email with both HTML and plain-text parts.

    subject      -- keep it plain, no emoji (emoji in subject is a common spam trigger)
    to_email     -- recipient
    heading      -- bold heading shown inside the email card
    body_lines   -- list of paragraph strings (already HTML-safe / no user-controlled markup)
    plain_text   -- full plain-text fallback version of the same message
    cta_text/cta_link -- optional button (e.g. "Reset Password" / link)
    """
    html_body = _build_html(heading, body_lines, cta_text, cta_link)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=fail_silently)
        return True
    except Exception as exc:
        logger.error(f"[Email] Failed to send '{subject}' to {to_email}: {exc}")
        if not fail_silently:
            raise
        return False
