import os
import re
from typing import Tuple
from .models import EmailRecord, ClassificationResult, Extraction, ResponseDraft
from google.generativeai import configure, GenerativeModel

# Configure Gemini once (if key exists)
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_KEY:
    configure(api_key=GEMINI_KEY)

def _heuristic_priority(subject: str, body: str) -> Tuple[str, int]:
    text = f"{subject} {body}".lower()
    urgent_words = ["urgent", "immediately", "asap", "critical", "cannot access", "down", "blocked", "error", "failed"]
    score = 5
    for w in urgent_words:
        if w in text:
            score = max(score, 9)
    return ("urgent" if score >= 8 else "not_urgent", score)

def _extract_contacts(body: str) -> Extraction:
    phones = re.findall(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}", body)
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", body)
    return Extraction(phone_numbers=list(set(phones)), emails=list(set(emails)), product_mentions=[], keywords=[])

def classify_with_gemini(email: EmailRecord) -> ClassificationResult:
    """
    Uses Gemini 1.5 Flash if GEMINI_API_KEY is present.
    Falls back to heuristics otherwise.
    """
    priority_tag, urgency = _heuristic_priority(email.subject, email.body)
    if not GEMINI_KEY:
        # Fallback classification
        sentiment = "negative" if any(k in (email.body or "").lower() for k in ["cannot", "unable", "error", "issue", "down"]) else "neutral"
        category = "CUSTOMER_SUPPORT"
        summary = (email.body or "").strip()[:200] or email.subject
        extraction = _extract_contacts(email.body or "")
        return ClassificationResult(
            summary=summary,
            category=category,
            sentiment=sentiment, priority=priority_tag, urgency_score=urgency,
            requires_response=True, confidence=0.6, extraction=extraction
        )

    prompt = f"""
You are an expert support triage assistant. Analyze this email and return STRICT JSON with keys:
summary, category, sentiment (positive|neutral|negative), priority (urgent|not_urgent), urgency_score (1-10),
requires_response (true|false), confidence (0-1), extraction: {{phone_numbers:[], emails:[], product_mentions:[], keywords:[]}}.

Email:
Subject: {email.subject}
From: {email.sender}
Body:
{email.body[:4000]}
"""
    model = GenerativeModel("gemini-1.5-flash")
    try:
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        # Best-effort: if model wrapped JSON in code fences
        text = text.strip("`").strip()
        import json
        data = json.loads(text)
        extraction = data.get("extraction") or {}
        return ClassificationResult(
            summary=data.get("summary") or email.subject,
            category=data.get("category", "CUSTOMER_SUPPORT"),
            sentiment=data.get("sentiment", "neutral"),
            priority=data.get("priority", priority_tag),
            urgency_score=int(data.get("urgency_score", urgency)),
            requires_response=bool(data.get("requires_response", True)),
            confidence=float(data.get("confidence", 0.7)),
            extraction=Extraction(
                phone_numbers=extraction.get("phone_numbers", []),
                emails=extraction.get("emails", []),
                product_mentions=extraction.get("product_mentions", []),
                keywords=extraction.get("keywords", []),
            ),
        )
    except Exception:
        # Fall back gracefully
        extraction = _extract_contacts(email.body or "")
        sentiment = "negative" if any(k in (email.body or "").lower() for k in ["cannot", "unable", "error", "issue", "down"]) else "neutral"
        return ClassificationResult(
            summary=(email.body or "").strip()[:200] or email.subject,
            category="CUSTOMER_SUPPORT",
            sentiment=sentiment,
            priority=priority_tag,
            urgency_score=urgency,
            requires_response=True,
            confidence=0.55,
            extraction=extraction,
        )

def generate_reply(email: EmailRecord, cls: ClassificationResult) -> ResponseDraft:
    tone = "professional"
    subj = f"Re: {email.subject}"
    empathy = ""
    if cls.sentiment == "negative":
        empathy = "I’m sorry you’re experiencing this—"
    body_lines = [
        f"Hi,",
        "",
        f"{empathy}Thanks for reaching out. Here's a quick summary of what I understand:",
        f"- {cls.summary}",
        "",
        "Next steps:",
        "- We’re reviewing your case now.",
    ]
    if cls.priority == "urgent":
        body_lines.append("- Prioritizing this as urgent; we’ll follow up shortly.")
    body_lines += [
        "",
        "Best regards,",
        "Support Team"
    ]
    auto_send = cls.confidence >= 0.85 and cls.priority == "not_urgent"
    return ResponseDraft(
        subject=subj,
        body="\n".join(body_lines),
        tone=tone,
        confidence=max(0.6, cls.confidence),
        auto_send_recommended=auto_send,
        reasoning="Template reply tuned to sentiment and priority."
    )
