"""
Microsoft Outlook tool for Voice AI Assistant.
Allows sending emails, reading inbox messages, and searching emails via Microsoft Graph.
"""
from __future__ import annotations
import json
from core.microsoft_client import get_microsoft_client

def outlook_action(parameters: dict) -> str:
    """Execute Microsoft Outlook operations."""
    action = parameters.get("action", "list_emails").lower()
    client = get_microsoft_client()

    if action == "send_email":
        to = parameters.get("to", "")
        subject = parameters.get("subject", "Message from AI Assistant")
        body = parameters.get("body", "")
        if not to or not body:
            return "Both 'to' recipient and email 'body' are required to send an Outlook email."
        result = client.send_outlook_email(to_recipients=to, subject=subject, body=body)
        return json.dumps(result, indent=2)

    elif action == "list_emails":
        top = int(parameters.get("top", 5))
        unread_only = bool(parameters.get("unread_only", False))
        result = client.list_outlook_emails(top=top, unread_only=unread_only)
        return json.dumps(result, indent=2)

    elif action == "search_emails":
        query = parameters.get("query", "")
        top = int(parameters.get("top", 5))
        if not query:
            return "Please provide a query keyword to search Outlook emails."
        result = client.search_outlook_emails(query=query, top=top)
        return json.dumps(result, indent=2)

    return f"Unknown Outlook action: {action}. Supported: send_email, list_emails, search_emails."


TOOL = {
    "name": "microsoft_outlook",
    "description": (
        "Interact with Microsoft Outlook. Send emails, read recent messages in inbox, "
        "or search emails by topic/sender. Call this when the user asks to send an email, "
        "check emails, read messages from Outlook, or search their mailbox."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "send_email | list_emails | search_emails",
            },
            "to": {
                "type": "STRING",
                "description": "Recipient email address(es) for send_email.",
            },
            "subject": {
                "type": "STRING",
                "description": "Subject line for send_email.",
            },
            "body": {
                "type": "STRING",
                "description": "Body content of the email.",
            },
            "query": {
                "type": "STRING",
                "description": "Keyword or sender to search for in search_emails.",
            },
            "unread_only": {
                "type": "BOOLEAN",
                "description": "If true, only unread emails will be listed.",
            },
            "top": {
                "type": "INTEGER",
                "description": "Maximum number of emails to retrieve (default: 5).",
            },
        },
        "required": ["action"],
    },
    "handler": outlook_action,
}
