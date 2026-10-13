"""
Microsoft Calendar tool for Voice AI Assistant.
Allows checking schedule/meetings and creating calendar appointments via Microsoft Graph.
"""
from __future__ import annotations
import json
from core.microsoft_client import get_microsoft_client

def calendar_action(parameters: dict) -> str:
    """Execute Microsoft Calendar operations."""
    action = parameters.get("action", "get_events").lower()
    client = get_microsoft_client()

    if action in ("get_events", "get_schedule", "list_events", "schedule"):
        days_ahead = int(parameters.get("days_ahead", 3))
        top = int(parameters.get("top", 5))
        result = client.get_calendar_events(days_ahead=days_ahead, top=top)
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
        "check appointments, or schedule new events. Call when user asks about their schedule, "
        "what meetings they have, or to book/schedule an appointment."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "get_events (default) | create_event",
            },
            "days_ahead": {
                "type": "INTEGER",
                "description": "Number of days ahead to look for meetings (default: 3).",
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
