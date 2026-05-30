import asyncio
import smtplib
from email.message import EmailMessage
from typing import Dict

from .config import settings


class EmailClient:
    """Lightweight Gmail SMTP sender.

    Gmail requires App Password authentication here, not your normal Gmail
    password. Enable 2-Step Verification in Google Account settings, create an
    App Password, then put it in EMAIL_PASS.
    """

    def __init__(self):
        self.email_user = settings.email_user
        self.email_pass = settings.email_pass
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587

    async def send_email(self, to_email: str, subject: str, body_text: str, body_html: str) -> Dict[str, str]:
        if not self.email_user or not self.email_pass:
            return {"status": "skipped", "reason": "EMAIL_USER and EMAIL_PASS are not configured."}

        message = self._build_message(to_email, subject, body_text, body_html)
        try:
            await asyncio.to_thread(self._send_blocking, message)
        except smtplib.SMTPException as exc:
            return {"status": "failed", "reason": str(exc)}
        return {"status": "sent"}

    def _build_message(self, to_email: str, subject: str, body_text: str, body_html: str) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self.email_user
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body_text)
        message.add_alternative(body_html, subtype="html")
        return message

    def _send_blocking(self, message: EmailMessage) -> None:
        # smtplib is blocking, so send_email runs this method in a worker thread.
        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(self.email_user, self.email_pass)
            smtp.send_message(message)
