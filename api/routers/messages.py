from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List
from core.database.session import get_session
from core.database.operations import (
    get_email_account_by_email,
    upsert_message,
    get_message_by_remote_id,
    bulk_add_extracted_codes,
)
from core.database.models import ExtractedCode
from api.auth import auth_required
from api.schemas import MessagesResponse, MessageItem, MessageDetailResponse
from utils.telegram import send_telegram_message, format_telegram_message
from utils.webhooks import trigger_webhooks_for_event
from core.mail_tm.client import MailTmClient
from core.extraction import CodeExtractor

router = APIRouter(prefix="/messages")


def get_db() -> Session:
    return get_session()


def get_client(request: Request) -> MailTmClient:
    return request.app.state.mail_client


@router.get("/{email}", response_model=MessagesResponse)
def list_messages(
    email: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    notify: bool = Query(default=False),
    preview_max: int | None = Query(default=None, ge=1, le=2000),
    auth=Depends(auth_required),
    db: Session = Depends(get_db),
    client: MailTmClient = Depends(get_client),
):
    acc = get_email_account_by_email(db, email)
    if not acc:
        raise HTTPException(status_code=404, detail="Email não encontrado")
    # Fetch messages from Mail.tm using token
    resp = client.session.get(
        f"{client.base_url}/messages",
        headers={"Authorization": f"Bearer {acc.token}"},
    )
    resp.raise_for_status()
    items_raw = resp.json().get("hydra:member", [])
    total = len(items_raw)
    sliced = items_raw[offset : offset + limit]
    items: List[MessageItem] = []
    for m in sliced:
        mid = m.get("id", "")
        subject = m.get("subject")
        sender = (m.get("from", {}) or {}).get("address")
        intro = m.get("intro")
        created_at = m.get("createdAt")
        # Persistir/atualizar no SQLite
        try:
            from datetime import datetime

            received_dt = None
            if created_at:
                try:
                    received_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                except Exception:
                    received_dt = None
            msg, created_flag = upsert_message(
                db,
                email_id=acc.id,
                remote_id=mid,
                sender=sender,
                subject=subject,
                text_preview=intro,
                received_at=received_dt,
            )
        except Exception:
            # Não bloquear resposta no caso de erro de persistência
            pass

        if notify and 'created_flag' in locals() and created_flag:
            try:
                text_fmt, parse_mode = format_telegram_message(subject, sender, intro, override_preview_max=preview_max)
                send_telegram_message(text=text_fmt, parse_mode=parse_mode)
            except Exception:
                pass

        # Disparo de webhooks para message.received quando nova mensagem inserida
        if 'created_flag' in locals() and created_flag:
            try:
                payload_evt = {
                    "event": "message.received",
                    "email": acc.email,
                    "message_id": mid,
                    "subject": subject,
                    "sender": sender,
                    "received_at": created_at,
                    "preview": intro,
                }
                trigger_webhooks_for_event(db, "message.received", payload_evt)
            except Exception:
                pass

        items.append(
            MessageItem(
                id=mid,
                subject=subject,
                sender=sender,
                received_at=intro or created_at,
            )
        )
    return MessagesResponse(email=acc.email, items=items, total=total, offset=offset, limit=limit)


@router.get("/db/{email}", response_model=MessagesResponse)
def list_messages_offline(
    email: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    sender: str | None = Query(default=None),
    subject_contains: str | None = Query(default=None),
    is_read: bool | None = Query(default=None),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    auth=Depends(auth_required),
    db: Session = Depends(get_db),
):
    from core.database.operations import list_messages_for_email
    acc = get_email_account_by_email(db, email)
    if not acc:
        raise HTTPException(status_code=404, detail="Email não encontrado")
    rows = list_messages_for_email(db, acc.id)
    # Filtros
    if sender:
        rows = [r for r in rows if (r.sender or "").lower() == sender.lower()]
    if subject_contains:
        rows = [r for r in rows if subject_contains.lower() in (r.subject or "").lower()]
    if is_read is not None:
        rows = [r for r in rows if bool(r.is_read) == bool(is_read)]
    # Ordenação
    rows = sorted(rows, key=lambda r: (r.received_at or 0), reverse=(order == "desc"))
    total = len(rows)
    sliced = rows[offset : offset + limit]
    items: List[MessageItem] = []
    for r in sliced:
        received_iso = r.received_at.isoformat() if r.received_at else None
        items.append(
            MessageItem(
                id=r.message_id_remote,
                subject=r.subject,
                sender=r.sender,
                received_at=received_iso,
            )
        )
    return MessagesResponse(email=acc.email, items=items, total=total, offset=offset, limit=limit)


@router.get("/db/{email}/{message_id}", response_model=MessageDetailResponse)
def get_message_detail_offline(
    email: str,
    message_id: str,
    auth=Depends(auth_required),
    db: Session = Depends(get_db),
):
    acc = get_email_account_by_email(db, email)
    if not acc:
        raise HTTPException(status_code=404, detail="Email não encontrado")
    row = get_message_by_remote_id(db, acc.id, message_id)
    if not row:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada no banco")
    received_iso = row.received_at.isoformat() if row.received_at else None
    return {
        "id": message_id,
        "subject": row.subject,
        "sender": row.sender,
        "text": row.full_text,
        "html": row.html_content,
        "received_at": received_iso,
        "email": acc.email,
    }


@router.get("/{email}/{message_id}", response_model=MessageDetailResponse)
def get_message_detail(
    email: str,
    message_id: str,
    notify: bool = Query(default=False),
    preview_max: int | None = Query(default=None, ge=1, le=2000),
    auth=Depends(auth_required),
    db: Session = Depends(get_db),
    client: MailTmClient = Depends(get_client),
):
    acc = get_email_account_by_email(db, email)
    if not acc:
        raise HTTPException(status_code=404, detail="Email não encontrado")
    try:
        resp = client.session.get(
            f"{client.base_url}/messages/{message_id}",
            headers={"Authorization": f"Bearer {acc.token}"},
        )
        resp.raise_for_status()
        detail = resp.json()
        subject = detail.get("subject")
        sender = (detail.get("from", {}) or {}).get("address")
        text = detail.get("text")
        html = detail.get("html")
        created_at = detail.get("createdAt")
        from datetime import datetime

        received_dt = None
        if created_at:
            try:
                received_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except Exception:
                received_dt = None
        msg, created_flag = upsert_message(
            db,
            email_id=acc.id,
            remote_id=message_id,
            sender=sender,
            subject=subject,
            full_text=text,
            html_content=html,
            received_at=received_dt,
        )
        if notify and created_flag:
            try:
                text_fmt, parse_mode = format_telegram_message(subject, sender, text or html, override_preview_max=preview_max)
                send_telegram_message(text=text_fmt, parse_mode=parse_mode)
            except Exception:
                pass

        # Disparo de webhooks para message.received quando nova mensagem inserida
        if created_flag:
            try:
                payload_evt = {
                    "event": "message.received",
                    "email": acc.email,
                    "message_id": message_id,
                    "subject": subject,
                    "sender": sender,
                    "received_at": created_at,
                    "text": text,
                }
                trigger_webhooks_for_event(db, "message.received", payload_evt)
            except Exception:
                pass
            
            # Extração automática de códigos da nova mensagem
            try:
                extractor = CodeExtractor(min_confidence=0.3)
                
                # Extrair do texto e HTML
                text_content = text or ""
                html_content = html or ""
                
                extracted_codes = []
                
                # Extrair do texto
                if text_content:
                    text_codes = extractor.extract_codes(text_content)
                    extracted_codes.extend(text_codes)
                
                # Extrair do HTML
                if html_content:
                    html_codes = extractor.extract_from_html(html_content)
                    extracted_codes.extend(html_codes)
                
                # Salvar códigos extraídos no banco
                if extracted_codes:
                    code_models = []
                    for code in extracted_codes:
                        code_model = ExtractedCode(
                            message_id=msg.id,
                            code=code.code,
                            code_type=code.code_type,
                            confidence=code.confidence,
                            context=code.context,
                            start_pos=code.start_pos,
                            end_pos=code.end_pos
                        )
                        code_models.append(code_model)
                    
                    bulk_add_extracted_codes(db, code_models)
                    
                    # Disparar webhook para code.extracted se houver códigos
                    try:
                        codes_payload = [
                            {
                                "code": code.code,
                                "type": code.code_type,
                                "confidence": code.confidence
                            }
                            for code in extracted_codes
                        ]
                        
                        code_event_payload = {
                            "event": "code.extracted",
                            "email": acc.email,
                            "message_id": message_id,
                            "subject": subject,
                            "sender": sender,
                            "codes": codes_payload
                        }
                        trigger_webhooks_for_event(db, "code.extracted", code_event_payload)
                    except Exception:
                        pass
                        
            except Exception:
                # Silently fail code extraction to not break message processing
                pass

        return {
            "id": message_id,
            "subject": subject,
            "sender": sender,
            "text": text,
            "html": html,
            "received_at": created_at,
            "email": acc.email,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha ao obter detalhe da mensagem: {e}")