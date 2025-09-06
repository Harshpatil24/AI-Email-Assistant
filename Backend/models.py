from __future__ import annotations
from typing import List, Optional, Literal, Dict
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

Sentiment = Literal["positive", "neutral", "negative"]
PriorityTag = Literal["urgent", "not_urgent"]

class EmailIn(BaseModel):
    sender: str
    subject: str
    body: str
    sent_date: datetime

class EmailRecord(BaseModel):
    id: str
    thread_id: Optional[str] = None
    sender: str
    subject: str
    body: str
    sent_date: datetime
    snippet: Optional[str] = None
    is_unread: bool = True
    source: Literal["gmail", "manual"] = "gmail"

class Extraction(BaseModel):
    phone_numbers: List[str] = []
    emails: List[str] = []
    product_mentions: List[str] = []
    keywords: List[str] = []

class ClassificationResult(BaseModel):
    summary: str
    category: str
    sentiment: Sentiment
    priority: PriorityTag
    urgency_score: int = Field(ge=1, le=10)
    requires_response: bool = True
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    extraction: Extraction = Field(default_factory=Extraction)

class ResponseDraft(BaseModel):
    subject: str
    body: str
    tone: Literal["professional", "casual", "concise"] = "professional"
    confidence: float = 0.7
    auto_send_recommended: bool = False
    reasoning: Optional[str] = None

class ProcessedEmail(BaseModel):
    record: EmailRecord
    classification: ClassificationResult
    draft: Optional[ResponseDraft] = None

class FetchOptions(BaseModel):
    max_results: int = 10
    hours_lookback: int = 48
    only_unread: bool = True
    query_terms: Optional[str] = None

class Stats(BaseModel):
    total_processed: int = 0
    drafts_created: int = 0
    emails_sent: int = 0
    categories: Dict[str, int] = {}
    last_run: Optional[str] = None
