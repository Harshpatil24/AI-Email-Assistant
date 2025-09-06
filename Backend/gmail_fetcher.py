import os
import base64
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .models import EmailRecord

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
]

class GmailClient:
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None

    def _ensure_auth(self):
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Missing {self.credentials_file}. Download OAuth client credentials from Google Cloud."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        self.service = build("gmail", "v1", credentials=creds)

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        def decode(b64: str) -> str:
            return base64.urlsafe_b64decode(b64.encode("utf-8")).decode("utf-8", errors="ignore")

        if payload.get("body", {}).get("data"):
            return decode(payload["body"]["data"])
        parts = payload.get("parts", []) or []
        text = ""
        for p in parts:
            mime = p.get("mimeType", "")
            if mime == "text/plain" and p.get("body", {}).get("data"):
                text += decode(p["body"]["data"])
            elif mime == "text/html" and p.get("body", {}).get("data") and not text:
                html = decode(p["body"]["data"])
                text = re.sub("<[^<]+?>", "", html)
        return text.strip()

    def fetch_recent(
        self, max_results: int = 10, hours_lookback: int = 48, only_unread: bool = True, query_terms: Optional[str] = None
    ) -> List[EmailRecord]:
        if self.service is None:
            self._ensure_auth()

        after_date = (datetime.utcnow() - timedelta(hours=hours_lookback)).strftime("%Y/%m/%d")
        query = f"after:{after_date}"
        if only_unread:
            query += " is:unread"
        if query_terms:
            query += f" {query_terms}"

        resp = self.service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = resp.get("messages", [])
        results: List[EmailRecord] = []

        for m in messages:
            msg = self.service.users().messages().get(userId="me", id=m["id"], format="full").execute()
            headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
            subject = headers.get("subject", "")
            sender = headers.get("from", "")
            date_str = headers.get("date", "")
            try:
                # Robust parse: take the RFC date upto seconds if TZ parsing fails
                timestamp = datetime.strptime(date_str[:25], "%a, %d %b %Y %H:%M:%S")
            except Exception:
                try:
                    timestamp = datetime.fromtimestamp(int(msg.get("internalDate", "0")) / 1000.0)
                except Exception:
                    timestamp = datetime.utcnow()

            body = self._extract_body(msg.get("payload", {}))
            snippet = msg.get("snippet", "")
            labels = msg.get("labelIds", [])
            is_unread = "UNREAD" in labels

            results.append(
                EmailRecord(
                    id=msg["id"],
                    thread_id=msg.get("threadId"),
                    sender=sender,
                    subject=subject,
                    body=body,
                    sent_date=timestamp,
                    snippet=snippet,
                    is_unread=is_unread,
                    source="gmail",
                )
            )
        return results
