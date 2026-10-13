"""
Microsoft 365 & WorkIQ Ecosystem Integration Client.

Handles Microsoft Graph API (Teams, Outlook, Calendar) and WorkIQ MCP Server connections.
Provides real API callers with graceful simulation fallbacks when credentials are placeholders.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import requests
from dotenv import dotenv_values
from memory.config_manager import BASE_DIR

ENV_FILE = BASE_DIR / ".env"

def _load_env_values() -> Dict[str, str]:
    """Load credentials exclusively from the project .env."""
    cfg = {key: value.strip() for key, value in dotenv_values(ENV_FILE, interpolate=False).items()
           if isinstance(value, str)}

    if cfg.get("MICROSOFT_ACCESS_TOKEN") and not cfg.get("MICROSOFT_GRAPH_TOKEN"):
        cfg["MICROSOFT_GRAPH_TOKEN"] = cfg["MICROSOFT_ACCESS_TOKEN"]

    return cfg


class MicrosoftClient:
    """
    Microsoft 365 and WorkIQ Connector.
    """

    GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self):
        self.config = _load_env_values()
        self.client_id = self.config.get("MICROSOFT_CLIENT_ID", "YOUR_MICROSOFT_CLIENT_ID")
        self.client_secret = self.config.get("MICROSOFT_CLIENT_SECRET", "YOUR_MICROSOFT_CLIENT_SECRET")
        self.tenant_id = self.config.get("MICROSOFT_TENANT_ID", "common")
        self.workiq_url = self.config.get("WORKIQ_MCP_SERVER_URL", "http://localhost:8080/mcp")
        self.workiq_key = self.config.get("WORKIQ_API_KEY", "YOUR_WORKIQ_API_KEY")
        self.graph_token = self.config.get("MICROSOFT_GRAPH_TOKEN", "")
        self._cached_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    def reload_config(self) -> None:
        self.config = _load_env_values()
        self.client_id = self.config.get("MICROSOFT_CLIENT_ID", "YOUR_MICROSOFT_CLIENT_ID")
        self.client_secret = self.config.get("MICROSOFT_CLIENT_SECRET", "YOUR_MICROSOFT_CLIENT_SECRET")
        self.tenant_id = self.config.get("MICROSOFT_TENANT_ID", "common")
        self.workiq_url = self.config.get("WORKIQ_MCP_SERVER_URL", "http://localhost:8080/mcp")
        self.workiq_key = self.config.get("WORKIQ_API_KEY", "YOUR_WORKIQ_API_KEY")
        self.graph_token = self.config.get("MICROSOFT_GRAPH_TOKEN", "")
        self._cached_token = None
        self._token_expires_at = 0.0

    def _acquire_token(self) -> Optional[str]:
        """Acquire a live Microsoft Graph Bearer token using OAuth2 Client Credentials flow."""
        if self.graph_token:
            return self.graph_token

        if self._cached_token and time.time() < self._token_expires_at:
            return self._cached_token

        if not (self.client_id and self.client_secret and self.tenant_id):
            return None

        placeholder_stems = ("YOUR_", "YOUR-", "PLACEHOLDER", "EXAMPLE", "CHANGE_ME")
        if any(p in self.client_id.upper() or p in self.client_secret.upper() for p in placeholder_stems):
            return None

        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "https://graph.microsoft.com/.default",
        }
        try:
            resp = requests.post(token_url, data=data, timeout=10)
            if resp.status_code == 200:
                body = resp.json()
                self._cached_token = body.get("access_token")
                expires_in = int(body.get("expires_in", 3600))
                self._token_expires_at = time.time() + max(60, expires_in - 300)
                return self._cached_token
            else:
                return None
        except Exception as e:
            print(f"[Microsoft 365] Token acquisition failed: {e}")
            return None

    def is_configured(self) -> bool:
        """Returns True if real credentials have been provided."""
        placeholder_stems = ("YOUR_", "YOUR-", "PLACEHOLDER", "EXAMPLE", "YOUR_AZURE", "YOUR_MICROSOFT", "CHANGE_ME")
        def _is_valid(val: str) -> bool:
            if not val or len(val.strip()) < 8:
                return False
            v_upper = val.strip().upper()
            return not any(p in v_upper for p in placeholder_stems)

        has_token = _is_valid(self.graph_token)
        has_app = _is_valid(self.client_id) and _is_valid(self.client_secret)
        return has_token or has_app

    def _get_headers(self) -> Dict[str, str]:
        token = self._acquire_token() or self.graph_token
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    # ── TEAMS ─────────────────────────────────────────────────────────────────

    def send_teams_message(self, recipient_or_chat_id: str, message: str, is_channel: bool = False, team_id: str = "") -> Dict[str, Any]:
        """Send message to a Microsoft Teams chat or channel."""
        if not self.is_configured():
            return {
                "status": "success (sandbox mode)",
                "note": "Microsoft credentials not configured in .env. Action simulated successfully.",
                "action": "send_teams_message",
                "target": recipient_or_chat_id,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }

        url = f"{self.GRAPH_BASE_URL}/chats/{recipient_or_chat_id}/messages"
        if is_channel and team_id:
            url = f"{self.GRAPH_BASE_URL}/teams/{team_id}/channels/{recipient_or_chat_id}/messages"

        payload = {"body": {"contentType": "text", "content": message}}
        try:
            resp = requests.post(url, headers=self._get_headers(), json=payload, timeout=10)
            if resp.status_code in (200, 201):
                return {"status": "success", "response": resp.json()}
            return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_teams_chats(self, top: int = 5) -> Dict[str, Any]:
        """List user's recent Microsoft Teams chats."""
        if not self.is_configured():
            return {
                "status": "success (sandbox mode)",
                "chats": [
                    {"id": "chat_001", "topic": "Engineering Sync", "last_message": "Release planned for Friday"},
                    {"id": "chat_002", "topic": "Product Strategy", "last_message": "Roadmap reviewed and approved"},
                    {"id": "chat_003", "topic": "General Discussion", "last_message": "Coffee chat at 4 PM"},
                ][:top],
                "note": "Configure MICROSOFT_CLIENT_ID in .env for live Microsoft 365 data.",
            }

        url = f"{self.GRAPH_BASE_URL}/me/chats?$top={top}&$expand=lastMessagePreview"
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                return {"status": "success", "chats": resp.json().get("value", [])}
            return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ── OUTLOOK EMAIL ─────────────────────────────────────────────────────────

    def send_outlook_email(self, to_recipients: List[str] | str, subject: str, body: str, is_html: bool = False) -> Dict[str, Any]:
        """Send email using Microsoft Outlook / Graph API."""
        if isinstance(to_recipients, str):
            to_recipients = [to_recipients]

        if not self.is_configured():
            return {
                "status": "success (sandbox mode)",
                "note": "Microsoft credentials not configured in .env. Email dispatch simulated.",
                "to": to_recipients,
                "subject": subject,
                "body_preview": body[:120],
                "sent_at": datetime.now().isoformat(),
            }

        recipients_list = [{"emailAddress": {"address": addr.strip()}} for addr in to_recipients]
        payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if is_html else "Text",
                    "content": body,
                },
                "toRecipients": recipients_list,
            },
            "saveToSentItems": "true",
        }
        url = f"{self.GRAPH_BASE_URL}/me/sendMail"
        try:
            resp = requests.post(url, headers=self._get_headers(), json=payload, timeout=12)
            if resp.status_code in (200, 202):
                return {"status": "success", "message": f"Email successfully sent to {', '.join(to_recipients)}"}
            return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_outlook_emails(self, top: int = 5, unread_only: bool = False) -> Dict[str, Any]:
        """List recent emails from Microsoft Outlook inbox."""
        if not self.is_configured():
            now = datetime.now()
            return {
                "status": "success (sandbox mode)",
                "emails": [
                    {
                        "id": "mail_01",
                        "sender": "sarah.connor@enterprise.com",
                        "subject": "Q3 Performance Review & Strategy",
                        "received": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
                        "preview": "Attached is the comprehensive summary for our executive meeting...",
                    },
                    {
                        "id": "mail_02",
                        "sender": "team-lead@techcorp.com",
                        "subject": "Sprint Retrospective Highlights",
                        "received": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
                        "preview": "Great work on completing the migration ahead of schedule...",
                    },
                ][:top],
                "note": "Set MICROSOFT_CLIENT_ID / MICROSOFT_GRAPH_TOKEN in .env for live inbox.",
            }

        filter_clause = "isRead eq false" if unread_only else ""
        url = f"{self.GRAPH_BASE_URL}/me/messages?$top={top}&$select=subject,sender,receivedDateTime,bodyPreview"
        if filter_clause:
            url += f"&$filter={filter_clause}"

        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                return {"status": "success", "emails": resp.json().get("value", [])}
            return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def search_outlook_emails(self, query: str, top: int = 5) -> Dict[str, Any]:
        """Search emails by keyword or sender."""
        if not self.is_configured():
            return {
                "status": "success (sandbox mode)",
                "query": query,
                "matches": [
                    {
                        "subject": f"Project Update mentioning '{query}'",
                        "sender": "colleague@company.com",
                        "snippet": f"...regarding our discussion on {query}, the documentation is ready...",
                    }
                ],
                "note": "Connected in sandbox mode. Set credentials in .env to search live Microsoft mailbox.",
            }

        url = f'{self.GRAPH_BASE_URL}/me/messages?$search="{query}"&$top={top}'
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                return {"status": "success", "emails": resp.json().get("value", [])}
            return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ── CALENDAR ─────────────────────────────────────────────────────────────

    def get_calendar_events(self, days_ahead: int = 3, top: int = 5) -> Dict[str, Any]:
        """Get upcoming calendar events / meetings."""
        if not self.is_configured():
            now = datetime.now()
            return {
                "status": "success (sandbox mode)",
                "events": [
                    {
                        "subject": "Microsoft 365 Architecture Review",
                        "start": (now + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
                        "end": (now + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
                        "organizer": "lead.architect@company.com",
                        "location": "Microsoft Teams Meeting",
                    },
                    {
                        "subject": "Weekly AI Assistant Standup",
                        "start": (now + timedelta(days=1, hours=10)).strftime("%Y-%m-%d %H:%M"),
                        "end": (now + timedelta(days=1, hours=10, minutes=30)).strftime("%Y-%m-%d %H:%M"),
                        "organizer": "pm@company.com",
                        "location": "Boardroom Alpha",
                    },
                ][:top],
                "note": "Sandbox mode. Configure Microsoft credentials in .env to sync your live calendar.",
            }

        start_iso = datetime.utcnow().isoformat() + "Z"
        end_iso = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"
        url = f"{self.GRAPH_BASE_URL}/me/calendarView?startDateTime={start_iso}&endDateTime={end_iso}&$top={top}&$select=subject,start,end,location,organizer"

        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                return {"status": "success", "events": resp.json().get("value", [])}
            return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_calendar_event(
        self, subject: str, start_time: str, end_time: str,
        attendees: Optional[List[str]] = None, location: str = "Teams Meeting", body: str = ""
    ) -> Dict[str, Any]:
        """Create a new calendar meeting or event."""
        if not self.is_configured():
            return {
                "status": "success (sandbox mode)",
                "subject": subject,
                "start": start_time,
                "end": end_time,
                "location": location,
                "attendees": attendees or [],
                "note": "Event created in sandbox mode. Configure Microsoft credentials in .env for live sync.",
            }

        att_list = [{"emailAddress": {"address": a.strip()}} for a in (attendees or [])]
        payload = {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "start": {"dateTime": start_time, "timeZone": "UTC"},
            "end": {"dateTime": end_time, "timeZone": "UTC"},
            "location": {"displayName": location},
            "attendees": att_list,
            "isOnlineMeeting": True if "teams" in location.lower() else False,
        }
        url = f"{self.GRAPH_BASE_URL}/me/events"
        try:
            resp = requests.post(url, headers=self._get_headers(), json=payload, timeout=10)
            if resp.status_code in (200, 201):
                return {"status": "success", "event": resp.json()}
            return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ── WORKIQ MCP & GRAPH COPILOT ───────────────────────────────────────────

    def query_workiq(self, query: str, scope: str = "all", max_results: int = 4) -> Dict[str, Any]:
        """
        Query WorkIQ MCP server / enterprise context.
        Enables cross-organizational intelligence across Teams, Outlook, and OneDrive.
        """
        if not self.is_configured() or not self.workiq_url or "localhost" in self.workiq_url:
            return {
                "status": "success (WorkIQ sandbox mode)",
                "query": query,
                "scope": scope,
                "results": [
                    {
                        "source": "Microsoft Teams / Architecture Channel",
                        "title": f"Recent decision regarding '{query}'",
                        "summary": f"Discussion confirmed deployment parameters and security guidelines for {query}.",
                    },
                    {
                        "source": "OneDrive / Enterprise Guidelines",
                        "title": f"WorkIQ Documentation on {query}",
                        "summary": f"Standard operating procedures and compliance standards relevant to {query}.",
                    },
                ],
                "note": "WorkIQ MCP server endpoint can be customized via WORKIQ_MCP_SERVER_URL in .env.",
            }

        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "workiq_search",
                    "arguments": {"query": query, "scope": scope, "limit": max_results},
                },
                "id": 1,
            }
            headers = {"Content-Type": "application/json"}
            if self.workiq_key and not self.workiq_key.startswith("YOUR_"):
                headers["Authorization"] = f"Bearer {self.workiq_key}"

            resp = requests.post(self.workiq_url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                return {"status": "success", "data": resp.json()}
            return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": f"WorkIQ MCP query failed: {e}"}

    # ── SHAREPOINT & ONEDRIVE ─────────────────────────────────────────────────

    def search_sharepoint_files(self, query: str, top: int = 5) -> Dict[str, Any]:
        """Search SharePoint sites, document libraries, and OneDrive files."""
        if not self.is_configured():
            return {
                "status": "success (sandbox mode)",
                "note": "Microsoft credentials not configured. Action simulated successfully.",
                "action": "search_sharepoint_files",
                "query": query,
                "matches": [
                    {
                        "name": f"{query}_Strategy_Doc.docx",
                        "webUrl": f"https://company.sharepoint.com/teams/general/docs/{query}_Strategy.docx",
                        "site": "General Enterprise",
                        "summary": f"Executive summary and key metrics regarding {query}.",
                    },
                    {
                        "name": f"{query}_Q3_Report.xlsx",
                        "webUrl": f"https://company.sharepoint.com/teams/finance/{query}_Q3.xlsx",
                        "site": "Finance Team",
                        "summary": f"Spreadsheet data and analytics for {query}.",
                    },
                ],
                "timestamp": datetime.now().isoformat(),
            }

        url = f"{self.GRAPH_BASE_URL}/search/query"
        payload = {
            "requests": [
                {
                    "entityTypes": ["driveItem", "site"],
                    "query": {"queryString": query},
                    "from": 0,
                    "size": top,
                }
            ]
        }
        try:
            resp = requests.post(url, headers=self._get_headers(), json=payload, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                containers = data.get("value", [{}])[0].get("hitsContainers", [{}])[0].get("hits", [])
                results = []
                for item in containers:
                    res = item.get("resource", {})
                    results.append({
                        "name": res.get("name", "Unknown"),
                        "webUrl": res.get("webUrl", ""),
                        "lastModified": res.get("lastModifiedDateTime", ""),
                        "summary": item.get("summary", ""),
                    })
                return {"status": "success", "count": len(results), "files": results}
            return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": f"SharePoint search failed: {e}"}

    def list_sharepoint_sites(self, query: str = "") -> Dict[str, Any]:
        """List accessible SharePoint sites within the enterprise."""
        if not self.is_configured():
            return {
                "status": "success (sandbox mode)",
                "action": "list_sharepoint_sites",
                "sites": [
                    {"name": "Engineering & Technology", "webUrl": "https://company.sharepoint.com/teams/eng"},
                    {"name": "Executive Leadership", "webUrl": "https://company.sharepoint.com/teams/exec"},
                    {"name": "Operations & Logistics", "webUrl": "https://company.sharepoint.com/teams/ops"},
                ],
            }

        url = f"{self.GRAPH_BASE_URL}/sites" + (f"?search={query}" if query else "")
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                sites = [{"name": s.get("displayName", s.get("name")), "webUrl": s.get("webUrl")} for s in resp.json().get("value", [])]
                return {"status": "success", "sites": sites}
            return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": f"SharePoint site query failed: {e}"}


# Shared singleton instance
_ms_client: Optional[MicrosoftClient] = None

def get_microsoft_client() -> MicrosoftClient:
    global _ms_client
    if _ms_client is None:
        _ms_client = MicrosoftClient()
    return _ms_client
