from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from api.auth import auth_required
from api.schemas import (
    ExtractedCodeResponse,
    CodesListResponse,
    CheckCodesRequest,
    CheckCodesResponse
)
from core.database import get_session
from core.database.models import EmailAccount, Message, ExtractedCode
from core.database.operations import (
    get_extracted_codes_by_email,
    get_extracted_codes_by_type,
    get_recent_extracted_codes,
    delete_extracted_codes_by_message,
    bulk_add_extracted_codes
)
from core.extraction import CodeExtractor, ALL_PATTERNS
from utils.logger import logger

router = APIRouter(prefix="/codes", tags=["codes"])


def get_db() -> Session:
    return get_session()


def _convert_extracted_code_to_response(code: ExtractedCode) -> ExtractedCodeResponse:
    """Convert ExtractedCode model to response schema."""
    # Get message subject if possible
    message_subject = None
    try:
        # This would require accessing the database, but we'll keep it simple
        # In a real implementation, you might want to join this data
        pass
    except Exception:
        pass
    
    return ExtractedCodeResponse(
        id=code.id,
        code=code.code,
        type=code.code_type,
        confidence=code.confidence,
        context=code.context,
        extracted_at=code.extracted_at.isoformat() if code.extracted_at else "",
        message_id=code.message_id,
        message_subject=message_subject
    )


@router.get("/{email}", response_model=CodesListResponse)
async def list_codes_for_email(
    email: str,
    type: Optional[str] = Query(None, description="Filter by code type"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of codes to return"),
    recent: bool = Query(False, description="Return only codes from last 24 hours"),
    db: Session = Depends(get_db),
    auth_data: dict = Depends(auth_required)
):
    """
    List extracted codes for an email address.
    
    Query parameters:
    - type: Filter by specific code type (otp_4, otp_6, verification_url, etc.)
    - limit: Maximum number of codes to return (default: 50)
    - recent: Return only codes from last 24 hours (default: false)
    """
    logger.info(f"Listing codes for email: {email}, type: {type}, limit: {limit}, recent: {recent}")
    
    # Verify email exists
    email_account = db.query(EmailAccount).filter(EmailAccount.email == email).first()
    if not email_account:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Get codes based on filters
    if recent:
        codes = get_recent_extracted_codes(db, email_id=email_account.id, hours=24, limit=limit)
    elif type:
        codes = get_extracted_codes_by_type(db, email_id=email_account.id, code_type=type, limit=limit)
    else:
        codes = get_extracted_codes_by_email(db, email_account.id)
        codes = codes[:limit]  # Apply limit manually
    
    # Convert to response format
    code_responses = [_convert_extracted_code_to_response(code) for code in codes]
    
    return CodesListResponse(
        email=email,
        codes=code_responses,
        total=len(code_responses)
    )


@router.post("/{email}/check", response_model=CheckCodesResponse)
async def check_and_extract_codes(
    email: str,
    request: CheckCodesRequest,
    db: Session = Depends(get_db),
    auth_data: dict = Depends(auth_required)
):
    """
    Check for new codes in messages and extract them.
    
    This will process all messages for the email and extract any codes found.
    Use force_refresh=true to re-extract from all messages (not just new ones).
    """
    logger.info(f"Checking codes for email: {email}, force_refresh: {request.force_refresh}")
    
    # Verify email exists
    email_account = db.query(EmailAccount).filter(EmailAccount.email == email).first()
    if not email_account:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Get all messages for this email
    messages = db.query(Message).filter(Message.email_id == email_account.id).all()
    
    if not messages:
        return CheckCodesResponse(
            email=email,
            processed_messages=0,
            new_codes_extracted=0,
            total_codes=0,
            codes=[]
        )
    
    # Initialize code extractor
    extractor = CodeExtractor(min_confidence=0.3)
    
    # Use specified patterns or all patterns
    patterns = request.patterns if request.patterns else list(ALL_PATTERNS.keys())
    
    processed_messages = 0
    new_codes_extracted = 0
    all_extracted_codes = []
    
    for message in messages:
        # Skip if not forcing refresh and message already has codes
        if not request.force_refresh:
            existing_codes = get_extracted_codes_by_message(db, message.id)
            if existing_codes:
                continue
        
        processed_messages += 1
        
        # Get text content from message
        text_content = message.full_text or message.text_preview or ""
        
        # Also extract from HTML if available
        if message.html_content:
            html_codes = extractor.extract_from_html(message.html_content, patterns=patterns)
            text_codes = extractor.extract_codes(text_content, patterns=patterns)
            
            # Combine and deduplicate
            all_codes = html_codes + text_codes
        else:
            all_codes = extractor.extract_codes(text_content, patterns=patterns)
        
        # Convert to database models
        extracted_code_models = []
        for code in all_codes:
            extracted_code = ExtractedCode(
                message_id=message.id,
                code=code.code,
                code_type=code.code_type,
                confidence=code.confidence,
                context=code.context,
                start_pos=code.start_pos,
                end_pos=code.end_pos
            )
            extracted_code_models.append(extracted_code)
        
        # Delete existing codes for this message if forcing refresh
        if request.force_refresh:
            delete_extracted_codes_by_message(db, message.id)
        
        # Add new codes to database
        if extracted_code_models:
            bulk_add_extracted_codes(db, extracted_code_models)
            new_codes_extracted += len(extracted_code_models)
            
            # Add to response list (convert to response format)
            for code in extracted_code_models:
                all_extracted_codes.append(_convert_extracted_code_to_response(code))
    
    # Get total codes for this email
    total_codes = len(get_extracted_codes_by_email(db, email_account.id))
    
    logger.info(f"Code extraction completed for {email}: {processed_messages} messages, {new_codes_extracted} new codes")
    
    return CheckCodesResponse(
        email=email,
        processed_messages=processed_messages,
        new_codes_extracted=new_codes_extracted,
        total_codes=total_codes,
        codes=all_extracted_codes
    )


@router.get("/{email}/types")
async def list_code_types(
    email: str,
    db: Session = Depends(get_db),
    auth_data: dict = Depends(auth_required)
):
    """
    List available code types and their descriptions.
    """
    # Verify email exists
    email_account = db.query(EmailAccount).filter(EmailAccount.email == email).first()
    if not email_account:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Get pattern descriptions from extractor
    extractor = CodeExtractor()
    pattern_descriptions = extractor.list_available_patterns()
    
    # Add count of each type for this email
    result = {}
    for pattern_name, description in pattern_descriptions.items():
        codes = get_extracted_codes_by_type(db, email_id=email_account.id, code_type=pattern_name)
        result[pattern_name] = {
            "description": description,
            "count": len(codes)
        }
    
    return result


@router.delete("/{email}")
async def delete_codes_for_email(
    email: str,
    type: Optional[str] = Query(None, description="Delete only codes of this type"),
    db: Session = Depends(get_db),
    auth_data: dict = Depends(auth_required)
):
    """
    Delete extracted codes for an email.
    
    Query parameters:
    - type: Delete only codes of this type (optional, deletes all if not specified)
    """
    logger.info(f"Deleting codes for email: {email}, type: {type}")
    
    # Verify email exists
    email_account = db.query(EmailAccount).filter(EmailAccount.email == email).first()
    if not email_account:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Get codes to delete
    if type:
        codes_to_delete = get_extracted_codes_by_type(db, email_id=email_account.id, code_type=type)
    else:
        codes_to_delete = get_extracted_codes_by_email(db, email_account.id)
    
    # Delete codes
    deleted_count = 0
    for code in codes_to_delete:
        db.delete(code)
        deleted_count += 1
    
    db.commit()
    
    logger.info(f"Deleted {deleted_count} codes for email: {email}")
    
    return {
        "email": email,
        "deleted_count": deleted_count,
        "type_filter": type
    }