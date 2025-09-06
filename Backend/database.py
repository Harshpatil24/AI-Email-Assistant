import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import EmailRecord, ClassificationResult, ResponseDraft, ProcessedEmail
import uuid

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "email_assistant.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with _conn() as con:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            thread_id TEXT,
            sender TEXT,
            subject TEXT,
            body TEXT,
            sent_date TEXT,
            snippet TEXT,
            is_unread INTEGER,
            source TEXT
        );""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS classifications (
            email_id TEXT PRIMARY KEY,
            summary TEXT,
            category TEXT,
            sentiment TEXT,
            priority TEXT,
            urgency_score INTEGER,
            requires_response INTEGER,
            confidence REAL,
            extraction_json TEXT,
            FOREIGN KEY(email_id) REFERENCES emails(id) ON DELETE CASCADE
        );""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS drafts (
            email_id TEXT PRIMARY KEY,
            subject TEXT,
            body TEXT,
            tone TEXT,
            confidence REAL,
            auto_send_recommended INTEGER,
            reasoning TEXT,
            FOREIGN KEY(email_id) REFERENCES emails(id) ON DELETE CASCADE
        );""")
        con.commit()

def upsert_email(record: EmailRecord):
    if not record.id:   #  auto-generate when missing
        record.id = str(uuid.uuid4())
    with _conn() as con:
        con.execute("""
        INSERT INTO emails (id, thread_id, sender, subject, body, sent_date, snippet, is_unread, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          thread_id=excluded.thread_id,
          sender=excluded.sender,
          subject=excluded.subject,
          body=excluded.body,
          sent_date=excluded.sent_date,
          snippet=excluded.snippet,
          is_unread=excluded.is_unread,
          source=excluded.source;
        """, (
            record.id, record.thread_id, record.sender, record.subject, record.body,
            record.sent_date.isoformat(), record.snippet, int(record.is_unread), record.source
        ))

def upsert_classification(email_id: str, cls: ClassificationResult):
    import json
    with _conn() as con:
        con.execute("""
        INSERT INTO classifications (email_id, summary, category, sentiment, priority, urgency_score,
            requires_response, confidence, extraction_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email_id) DO UPDATE SET
          summary=excluded.summary,
          category=excluded.category,
          sentiment=excluded.sentiment,
          priority=excluded.priority,
          urgency_score=excluded.urgency_score,
          requires_response=excluded.requires_response,
          confidence=excluded.confidence,
          extraction_json=excluded.extraction_json;
        """, (
            email_id, cls.summary, cls.category, cls.sentiment, cls.priority,
            cls.urgency_score, int(cls.requires_response), cls.confidence,
            json.dumps(cls.extraction.dict())
        ))

def upsert_draft(email_id: str, draft: ResponseDraft):
    with _conn() as con:
        con.execute("""
        INSERT INTO drafts (email_id, subject, body, tone, confidence, auto_send_recommended, reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email_id) DO UPDATE SET
          subject=excluded.subject,
          body=excluded.body,
          tone=excluded.tone,
          confidence=excluded.confidence,
          auto_send_recommended=excluded.auto_send_recommended,
          reasoning=excluded.reasoning;
        """, (
            email_id, draft.subject, draft.body, draft.tone, draft.confidence,
            int(draft.auto_send_recommended), draft.reasoning
        ))

def list_processed(limit: int = 100) -> List[ProcessedEmail]:
    import json
    with _conn() as con:
        rows = con.execute("""
        SELECT e.id, e.thread_id, e.sender, e.subject, e.body, e.sent_date, e.snippet, e.is_unread, e.source,
               c.summary, c.category, c.sentiment, c.priority, c.urgency_score, c.requires_response, c.confidence, c.extraction_json,
               d.subject, d.body, d.tone, d.confidence, d.auto_send_recommended, d.reasoning
        FROM emails e
        LEFT JOIN classifications c ON c.email_id = e.id
        LEFT JOIN drafts d ON d.email_id = e.id
        ORDER BY datetime(e.sent_date) DESC
        LIMIT ?;""", (limit,)).fetchall()

    result: List[ProcessedEmail] = []
    for r in rows:
        (eid, thr, snd, sub, body, sdate, snip, unread, source,
         csum, ccat, csent, cpri, curg, creq, cconf, cext,
         dsubj, dbody, dtone, dconf, dauto, dreas) = r

        record = EmailRecord(
            id=eid, thread_id=thr, sender=snd, subject=sub, body=body,
            sent_date=datetime.fromisoformat(sdate), snippet=snip, is_unread=bool(unread), source=source
        )
        classification = None
        if csum is not None:
            from .models import Extraction, ClassificationResult
            import json
            extraction = Extraction(**(json.loads(cext) if cext else {}))
            classification = ClassificationResult(
                summary=csum, category=ccat, sentiment=csent,
                priority=cpri, urgency_score=curg, requires_response=bool(creq),
                confidence=cconf, extraction=extraction
            )
        draft = None
        if dsubj is not None:
            from .models import ResponseDraft
            draft = ResponseDraft(
                subject=dsubj, body=dbody, tone=dtone or "professional",
                confidence=dconf or 0.7, auto_send_recommended=bool(dauto), reasoning=dreas
            )
        result.append(ProcessedEmail(record=record, classification=classification, draft=draft))
    return result

def get_counts_by_category() -> Dict[str, int]:
    with _conn() as con:
        rows = con.execute("""
        SELECT category, COUNT(*) FROM classifications GROUP BY category;
        """).fetchall()
    return {k: v for k, v in rows}
