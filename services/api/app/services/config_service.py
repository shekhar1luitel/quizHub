from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.organization import AppConfig
from app.schemas.management import MailConfigIn, MailConfigOut


MAIL_CONFIG_KEY = "mail.smtp"


class ConfigService:
    def __init__(self, db: Session):
        self.db = db

    def get_mail_config(self) -> MailConfigOut:
        record = self.db.get(AppConfig, MAIL_CONFIG_KEY)
        base = settings.mail_settings.copy()
        if record and record.value_json:
            base.update(record.value_json)

        is_configured = bool(base.get("host") and base.get("from_email"))
        return MailConfigOut(**base, is_configured=is_configured)

    def save_mail_config(self, data: MailConfigIn) -> MailConfigOut:
        record = self.db.get(AppConfig, MAIL_CONFIG_KEY)
        payload = data.model_dump()

        if record is None:
            record = AppConfig(
                key=MAIL_CONFIG_KEY,
                value_json=payload,
                scope="global",
            )
            self.db.add(record)
        else:
            record.value_json = payload

        self.db.flush()
        return self.get_mail_config()
