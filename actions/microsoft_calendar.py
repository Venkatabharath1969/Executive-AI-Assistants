"""
Microsoft Calendar tool for Voice AI Assistant.
Checks schedule/meetings, creates appointments, and falls back to local agenda
files for board members whose live calendar returns nothing.
"""
from __future__ import annotations
import json
import os
import re
from pathlib import Path
from core.microsoft_client import get_microsoft_client

# Agenda files live here: memory/agendas/<person_slug>.json|pdf|docx
_AGENDA_DIR = Path(__file__).resolve().parent.parent / "memory" / "agendas"
_BOARD_MEMBERS: frozenset[str] = frozenset({
    "bharath", "bharat", "kumar", "venkatabharath",
})


def _person_slug(name: str) -> str:
    """'Bharath Kumar' → 'bharath_kumar'"""
    return re.sub(r"\s+", "_", name.strip().lower())


def _is_board_member(name: str) -> bool:
    slug = _person_slug(name)
    return any(bm in slug for bm in _BOARD_MEMBERS)


def _load_agenda(name: str) -> str | None:
    """Return agenda text from memory/agendas/<slug>.json, or None if absent."""
    slug = _person_slug(name)
    for ext in (".json", ".txt"):
        p = _AGENDA_DIR / f"{slug}{ext}"
        if p.exists():
            try:
                return p.read_text(encoding="utf-8")
            except OSError:
                pass

    # Try pdf/docx if available importers exist
    for ext in (".pdf", ".docx"):
        p = _AGENDA_DIR / f"{slug}{ext}"
        if p.exists():
            try:
                if ext == ".pdf":
                    import pypdf
                    reader = pypdf.PdfReader(str(p))
                    return "\n".join(page.extract_text() or "" for page in reader.pages)
                if ext == ".docx":
                    import docx
                    doc = docx.Document(str(p))
                    return "\n".join(para.text for para in doc.paragraphs)
            except Exception:
                pass
    return None


def calendar_action(parameters: dict) -> str:
    """Execute Microsoft Calendar operations."""
    action = parameters.get("action", "get_events").lower()
    person = parameters.get("person", "").strip()
    client = get_microsoft_client()

    if action in ("get_events", "get_schedule", "list_events", "schedule"):
        days_ahead = int(parameters.get("days_ahead", 7 if person else 3))
        top = int(parameters.get("top", 5))
        result = client.get_calendar_events(days_ahead=days_ahead, top=top)

        # Agenda fallback: board member with empty live calendar
        events = result.get("value", result) if isinstance(result, dict) else result
        has_events = bool(events) and not (isinstance(events, list) and len(events) == 0)

        if person and _is_board_member(person) and not has_events:
            agenda_text = _load_agenda(person)
            if agenda_text:
                return json.dumps({
                    "source": "agenda_file",
                    "person": person,
                    "note": (
                        f"Live calendar for {person} returned no events. "
                        "Showing agenda from local file."
                    ),
                    "agenda": agenda_text,
                }, indent=2)
            return json.dumps({
                "source": "live_calendar",
                "person": person,
                "value": [],
                "note": (
                    f"No upcoming events found for {person} and no local "
                    f"agenda file at memory/agendas/{_person_slug(person)}.json"
                ),
            }, indent=2)

        return json.dumps(result, indent=2)

    elif action == "create_event":
        subject = parameters.get("subject", "Meeting")
        start_time = parameters.get("start_time", "")
        end_time = parameters.get("end_time", "")
        location = parameters.get("location", "Microsoft Teams Meeting")
        attendees = parameters.get("attendees", [])
        if isinstance(attendees, str):
            attendees = [a.strip() for a in attendees.split(",") if a.strip()]
        body = parameters.get("body", "")

        if not start_time or not end_time:
            return "Both start_time and end_time (in ISO format, e.g. '2026-10-10T14:00:00') are required."

        result = client.create_calendar_event(
            subject=subject,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
            location=location,
            body=body,
        )
        return json.dumps(result, indent=2)

    return f"Unknown Calendar action: {action}. Supported: get_events, create_event."


TOOL = {
    "name": "microsoft_calendar",
    "description": (
        "Interact with Microsoft Calendar / Outlook schedule. Retrieve upcoming meetings, "
        "check appointments, or schedule new events. For board members with empty live "
        "calendars, automatically falls back to agenda files in memory/agendas/. "
        "Call when user asks about their schedule, someone's availability, what meetings "
        "they have, or to book/schedule an appointment."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "get_events (default) | create_event",
            },
            "person": {
                "type": "STRING",
                "description": (
                    "Name of the person whose calendar to check (e.g. 'Bharath Kumar'). "
                    "For board members with no live events, agenda files are used as fallback."
                ),
            },
            "days_ahead": {
                "type": "INTEGER",
                "description": "Number of days ahead to look for meetings (default: 3, or 7 when person is set).",
            },
            "top": {
                "type": "INTEGER",
                "description": "Maximum number of events to return.",
            },
            "subject": {
                "type": "STRING",
                "description": "Meeting subject for create_event.",
            },
            "start_time": {
                "type": "STRING",
                "description": "Start time in ISO format (e.g. 2026-10-10T15:00:00).",
            },
            "end_time": {
                "type": "STRING",
                "description": "End time in ISO format (e.g. 2026-10-10T16:00:00).",
            },
            "attendees": {
                "type": "STRING",
                "description": "Comma-separated list of attendee email addresses.",
            },
            "location": {
                "type": "STRING",
                "description": "Location name or 'Microsoft Teams Meeting'.",
            },
            "body": {
                "type": "STRING",
                "description": "Description or agenda of the meeting.",
            },
        },
        "required": ["action"],
    },
    "handler": calendar_action,
}
