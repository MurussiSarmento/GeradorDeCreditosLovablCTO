from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, Float
from datetime import datetime, timezone


Base = declarative_base()


class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    account_id = Column(String, nullable=False)
    password_encrypted = Column(String, nullable=False)
    token = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_checked_at = Column(DateTime, nullable=True)
    status = Column(String, default="active")
    message_count = Column(Integer, default=0)


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    email_id = Column(String, nullable=False)
    message_id_remote = Column(String, nullable=False)
    sender = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    text_preview = Column(String, nullable=True)
    full_text = Column(Text, nullable=True)
    html_content = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    received_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    events = Column(Text, nullable=False)  # JSON array como texto
    secret_key = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_triggered_at = Column(DateTime, nullable=True)
    failures = Column(Integer, default=0)


class ExtractedCode(Base):
    __tablename__ = "extracted_codes"

    id = Column(String, primary_key=True)
    message_id = Column(String, nullable=False)
    code = Column(String, nullable=False)
    code_type = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    context = Column(Text, nullable=True)
    start_pos = Column(Integer, default=0)
    end_pos = Column(Integer, default=0)
    extracted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))