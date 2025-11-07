from typing import Optional, List, Tuple
import json
import uuid
from sqlalchemy.orm import Session
from core.database.models import EmailAccount, Message, Webhook, ExtractedCode


def add_email_account(db: Session, account: EmailAccount) -> None:
    db.add(account)
    db.commit()


def get_email_account_by_email(db: Session, email: str) -> Optional[EmailAccount]:
    return db.query(EmailAccount).filter(EmailAccount.email == email).one_or_none()


def get_message_by_remote_id(db: Session, email_id: str, remote_id: str) -> Optional[Message]:
    return (
        db.query(Message)
        .filter(Message.email_id == email_id, Message.message_id_remote == remote_id)
        .one_or_none()
    )


def upsert_message(
    db: Session,
    email_id: str,
    remote_id: str,
    sender: Optional[str] = None,
    subject: Optional[str] = None,
    text_preview: Optional[str] = None,
    received_at=None,
    full_text: Optional[str] = None,
    html_content: Optional[str] = None,
) -> Tuple[Message, bool]:
    msg = get_message_by_remote_id(db, email_id, remote_id)
    if msg is None:
        # Usar remote_id como id local por simplicidade se único por email
        msg = Message(
            id=f"{email_id}:{remote_id}",
            email_id=email_id,
            message_id_remote=remote_id,
            sender=sender,
            subject=subject,
            text_preview=text_preview,
            received_at=received_at,
            full_text=full_text,
            html_content=html_content,
        )
        db.add(msg)
        created = True
    else:
        msg.sender = sender or msg.sender
        msg.subject = subject or msg.subject
        msg.text_preview = text_preview or msg.text_preview
        msg.received_at = received_at or msg.received_at
        msg.full_text = full_text or msg.full_text
        msg.html_content = html_content or msg.html_content
        created = False
    db.commit()
    return msg, created


def list_messages_for_email(db: Session, email_id: str) -> List[Message]:
    return db.query(Message).filter(Message.email_id == email_id).all()


def get_active_webhooks_for_event(db: Session, event_name: str) -> List[Webhook]:
    """Retorna webhooks ativos que estão inscritos no evento fornecido.
    Como os eventos são armazenados em texto JSON, filtramos em Python.
    """
    hooks = db.query(Webhook).filter(Webhook.active == True).all()
    result: List[Webhook] = []
    for h in hooks:
        try:
            events = json.loads(h.events or "[]")
            if event_name in events:
                result.append(h)
        except Exception:
            # Ignorar webhooks com eventos inválidos
            continue
    return result


# ExtractedCode operations
def add_extracted_code(db: Session, code: ExtractedCode) -> None:
    """Add a new extracted code to the database."""
    if not code.id:
        code.id = str(uuid.uuid4())
    db.add(code)
    db.commit()


def get_extracted_codes_by_message(db: Session, message_id: str) -> List[ExtractedCode]:
    """Get all extracted codes for a specific message."""
    return db.query(ExtractedCode).filter(ExtractedCode.message_id == message_id).all()


def get_extracted_codes_by_email(db: Session, email_id: str) -> List[ExtractedCode]:
    """Get all extracted codes for all messages of an email."""
    return (
        db.query(ExtractedCode)
        .join(Message, ExtractedCode.message_id == Message.id)
        .filter(Message.email_id == email_id)
        .order_by(ExtractedCode.extracted_at.desc())
        .all()
    )


def get_extracted_codes_by_type(
    db: Session, 
    email_id: Optional[str] = None,
    code_type: Optional[str] = None,
    limit: Optional[int] = None
) -> List[ExtractedCode]:
    """Get extracted codes filtered by email and/or type."""
    query = db.query(ExtractedCode)
    
    if email_id:
        query = query.join(Message, ExtractedCode.message_id == Message.id).filter(Message.email_id == email_id)
    
    if code_type:
        query = query.filter(ExtractedCode.code_type == code_type)
    
    query = query.order_by(ExtractedCode.extracted_at.desc())
    
    if limit:
        query = query.limit(limit)
    
    return query.all()


def get_recent_extracted_codes(
    db: Session, 
    email_id: Optional[str] = None,
    hours: int = 24,
    limit: int = 50
) -> List[ExtractedCode]:
    """Get recently extracted codes."""
    from datetime import datetime, timezone, timedelta
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    query = db.query(ExtractedCode).filter(ExtractedCode.extracted_at >= cutoff_time)
    
    if email_id:
        query = query.join(Message, ExtractedCode.message_id == Message.id).filter(Message.email_id == email_id)
    
    return query.order_by(ExtractedCode.extracted_at.desc()).limit(limit).all()


def delete_extracted_codes_by_message(db: Session, message_id: str) -> int:
    """Delete all extracted codes for a message. Returns count of deleted records."""
    count = db.query(ExtractedCode).filter(ExtractedCode.message_id == message_id).count()
    db.query(ExtractedCode).filter(ExtractedCode.message_id == message_id).delete()
    db.commit()
    return count


def bulk_add_extracted_codes(db: Session, codes: List[ExtractedCode]) -> None:
    """Add multiple extracted codes in bulk."""
    for code in codes:
        if not code.id:
            code.id = str(uuid.uuid4())
    
    db.add_all(codes)
    db.commit()