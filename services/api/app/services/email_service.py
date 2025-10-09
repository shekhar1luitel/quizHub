from __future__ import annotations

import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import EmailEvent
from app.schemas.management import EmailDispatchResult
from app.services.config_service import ConfigService


class EmailService:
    def __init__(self, db: Session):
        self.db = db
        self.config_service = ConfigService(db)

    def enqueue(
        self,
        *,
        to_email: str,
        template: str,
        payload: dict | None = None,
    ) -> EmailEvent:
        event = EmailEvent(
            to_email=to_email,
            template=template,
            payload_json=payload or {},
        )
        self.db.add(event)
        self.db.flush()
        return event

    def dispatch_pending(self, limit: int = 20) -> EmailDispatchResult:
        stmt = (
            select(EmailEvent)
            .where(EmailEvent.status == "queued")
            .order_by(EmailEvent.created_at.asc())
            .limit(limit)
        )
        events = self.db.scalars(stmt).all()

        processed = 0
        sent = 0
        failed = 0
        errors: list[str] = []

        config = self.config_service.get_mail_config()
        if not config.is_configured:
            raise RuntimeError("Mail configuration is incomplete; update config before dispatching emails.")

        for event in events:
            processed += 1
            try:
                self._send_event(event, config)
                event.status = "sent"
                event.sent_at = datetime.now(timezone.utc)
                event.error_msg = None
                sent += 1
            except Exception as exc:  # noqa: BLE001
                event.status = "failed"
                event.error_msg = str(exc)
                failed += 1
                errors.append(f"event {event.id}: {exc}")

        self.db.flush()
        return EmailDispatchResult(
            processed=processed,
            sent=sent,
            failed=failed,
            errors=errors,
        )

    def _send_event(self, event: EmailEvent, config) -> None:
        if not config.host or not config.from_email:
            raise RuntimeError("Mail configuration incomplete; host and from_email are required.")

        subject, body = self._render_template(event.template, event.payload_json or {})
        message = EmailMessage()
        message["Subject"] = subject
        if config.from_name:
            message["From"] = f"{config.from_name} <{config.from_email}>"
        else:
            message["From"] = config.from_email
        message["To"] = event.to_email
        message.set_content(body)

        host = config.host
        port = config.port or 587

        server = smtplib.SMTP(host, port, timeout=20)
        server.ehlo()
        if config.tls_ssl:
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.ehlo()

        try:
            if config.username:
                password = config.password or ""
                server.login(config.username, password)
            server.send_message(message)
        finally:
            try:
                server.quit()
            except Exception:  # noqa: BLE001
                pass

    def _render_template(self, template: str, payload: dict) -> tuple[str, str]:
        if template == "email_verification":
            username = payload.get("username", "Learner")
            code = payload.get("code", "")
            subject = "Verify your QuizMaster email"
            body = (
                f"Hi {username},\n\n"
                "Use the verification code below to activate your account:\n\n"
                f"{code}\n\n"
                "This code expires shortly. If you did not request this, you can ignore the message.\n\n"
                "— QuizMaster Team"
            )
            return subject, body

        if template == "admin_user_invite":
            username = payload.get("username", "Team member")
            subject = "Your QuizMaster admin access is ready"
            body = (
                f"Hello {username},\n\n"
                "An administrator has set up an account for you on QuizMaster. Sign in with the email address "
                "that received this invitation and the temporary password provided to you.\n\n"
                "Once you log in, update your password and review the organization settings.\n\n"
                "— QuizMaster Team"
            )
            return subject, body

        subject = payload.get("subject", template.replace("_", " ").title())
        body = payload.get(
            "body",
            "This is an automated message from QuizMaster. No additional content was provided.",
        )
        return subject, body
