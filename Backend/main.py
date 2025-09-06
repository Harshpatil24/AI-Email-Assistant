from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime, timedelta
import os

from .models import (
    EmailIn, EmailRecord, ClassificationResult, ResponseDraft,
    ProcessedEmail, FetchOptions, Stats
)
from .gmail_fetcher import GmailClient
from .ai_classifier import classify_with_gemini, generate_reply
from .priority_queue import email_queue
from . import database as db

app = FastAPI(title="AI Email Assistant Backend", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Backend is working!"}

# Allow local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    db.init_db()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "gmail_credentials_json_exists": os.path.exists("credentials.json"),
        "token_exists": os.path.exists("token.json"),
        "gemini_key_present": bool(os.getenv("GEMINI_API_KEY", "")),
        "time": datetime.utcnow().isoformat() + "Z",
    }

@app.post("/emails/fetch", response_model=List[ProcessedEmail])
def fetch_and_process(options: FetchOptions):
    """
    Fetch recent Gmail emails, classify & prioritize them, store in DB, return the processed list.
    """
    client = GmailClient()
    emails = client.fetch_recent(
        max_results=options.max_results,
        hours_lookback=options.hours_lookback,
        only_unread=options.only_unread,
        query_terms=options.query_terms,
    )

    processed: List[ProcessedEmail] = []
    for rec in emails:
        db.upsert_email(rec)
        cls: ClassificationResult = classify_with_gemini(rec)
        draft: ResponseDraft = generate_reply(rec, cls)

        db.upsert_classification(rec.id, cls)
        db.upsert_draft(rec.id, draft)

        p = ProcessedEmail(record=rec, classification=cls, draft=draft)
        processed.append(p)
        email_queue.push(p)

    return processed

@app.get("/emails", response_model=List[ProcessedEmail])
def list_emails(limit: int = 100):
    return db.list_processed(limit=limit)

@app.get("/emails/queue/next", response_model=ProcessedEmail | None)
def next_email():
    return email_queue.pop()

@app.post("/process", response_model=ProcessedEmail)
def process_manual(email: EmailIn):
    """
    Accept a raw email (e.g., from CSV or webhook), classify and enqueue.
    """
    record = EmailRecord(
        id=f"manual-{int(datetime.utcnow().timestamp()*1000)}",
        thread_id=None,
        sender=email.sender,
        subject=email.subject,
        body=email.body,
        sent_date=email.sent_date,
        snippet=(email.body or "")[:140],
        is_unread=True,
        source="manual",
    )
    db.upsert_email(record)
    cls = classify_with_gemini(record)
    draft = generate_reply(record, cls)
    db.upsert_classification(record.id, cls)
    db.upsert_draft(record.id, draft)
    p = ProcessedEmail(record=record, classification=cls, draft=draft)
    email_queue.push(p)
    return p

@app.get("/stats", response_model=Stats)
def stats():
    cats = db.get_counts_by_category()
    # simple derived stats
    processed = sum(cats.values())
    return Stats(
        total_processed=processed,
        drafts_created=processed,  # 1:1 with processed in this design
        emails_sent=0,             # wire up later to send email
        categories=cats,
        last_run=datetime.utcnow().isoformat() + "Z",
    )
