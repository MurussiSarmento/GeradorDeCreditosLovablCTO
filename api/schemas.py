from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from typing import Any


class EmailCreateRequest(BaseModel):
    domain: Optional[str] = Field(default=None, description="Domínio opcional para o email")


class EmailResponse(BaseModel):
    email: EmailStr
    domain: str
    status: str
    created_at: float


class EmailDetailResponse(EmailResponse):
    account_id: str


class EmailListItem(BaseModel):
    email: EmailStr
    domain: str
    created_at: float
    status: str
    message_count: int | None = None
    last_checked_at: float | None = None

class Pagination(BaseModel):
    total: int
    skip: int
    limit: int
    page: int
    pages: int
    has_next: bool
    has_previous: bool


class EmailsListResponse(BaseModel):
    items: List[EmailListItem]
    pagination: Pagination


class MessageItem(BaseModel):
    id: str
    subject: Optional[str]
    sender: Optional[str]
    received_at: Optional[str]


class MessagesResponse(BaseModel):
    email: EmailStr
    items: List[MessageItem]
    total: int
    offset: int
    limit: int


class MessageDetailResponse(BaseModel):
    id: str
    subject: Optional[str]
    sender: Optional[str]
    text: Optional[str]
    html: Optional[str]
    received_at: Optional[str]
    email: EmailStr


class GenerateEmailsRequest(BaseModel):
    quantity: int = Field(ge=1, le=10000, description="Número de emails a criar")
    unique_domains: bool = Field(default=True, description="Tentar domínios distintos")
    auto_delete_seconds: Optional[int] = Field(default=None, ge=300, le=86400)
    sync: bool = Field(default=False, description="Executa criação de forma síncrona e retorna resultado")
    webhook_url: Optional[str] = Field(default=None, description="URL para notificação via webhook ao concluir")
    webhook_secret: Optional[str] = Field(default=None, description="Segredo opcional para assinatura HMAC do webhook opcional")


class GenerateEmailsResponse(BaseModel):
    job_id: str
    status: str
    polling_url: str


class GenerateEmailsBatchResponse(BaseModel):
    emails: List[dict]
    total: int
    created_in_seconds: float
    batch_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[float] = None
    eta_seconds: Optional[float] = None
    duration_seconds: Optional[float] = None
    result: Optional[List[dict]] = None
    error: Optional[str] = None


class WebhookRegisterRequest(BaseModel):
    url: str
    events: List[str]
    secret_key: Optional[str] = None


class WebhookResponse(BaseModel):
    webhook_id: str
    url: str
    events: List[str]
    active: bool
    created_at: str
    last_triggered_at: Optional[str] = None
    failures: int = 0


class WebhooksListResponse(BaseModel):
    webhooks: List[WebhookResponse]
    total: int


# Code extraction schemas
class ExtractedCodeResponse(BaseModel):
    id: str
    code: str
    type: str
    confidence: float
    context: Optional[str] = None
    extracted_at: str
    message_id: Optional[str] = None
    message_subject: Optional[str] = None


class CodesListResponse(BaseModel):
    email: EmailStr
    codes: List[ExtractedCodeResponse]
    total: int


class CheckCodesRequest(BaseModel):
    force_refresh: bool = Field(default=False, description="Force re-extraction from all messages")
    patterns: Optional[List[str]] = Field(default=None, description="Specific patterns to extract (default: all)")


class CheckCodesResponse(BaseModel):
    email: EmailStr
    processed_messages: int
    new_codes_extracted: int
    total_codes: int
    codes: List[ExtractedCodeResponse]