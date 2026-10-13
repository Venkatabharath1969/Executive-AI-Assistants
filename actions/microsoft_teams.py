"""
Microsoft Teams tool for Voice AI Assistant.
Allows sending messages to Teams chats/channels and reading recent messages.
"""
from __future__ import annotations
import json
from core.microsoft_client import get_microsoft_client

def teams_action(parameters: dict) -> str:
    """Execute Microsoft Teams operations."""
    action = parameters.get("action", "send_message").lower()
    client = get_microsoft_client()

    if action == "send_message":
        recipient = parameters.get("recipient_or_channel", "")
        message = parameters.get("message", "")
        is_channel = parameters.get("is_channel", False)
        team_id = parameters.get("team_id", "")
        if not message:
            return "Please provide the message text to send to Microsoft Teams."
        result = client.send_teams_message(recipient or "general", message, is_channel=is_channel, team_id=team_id)
        return json.dumps(result, indent=2)

    elif action == "list_chats":
        top = int(parameters.get("top", 5))
        result = client.list_teams_chats(top=top)
        return json.dumps(result, indent=2)

    return f"Unknown Teams action: {action}. Supported: send_message, list_chats."


TOOL = {
    "name": "microsoft_teams",
    "description": (
        "Interact with Microsoft Teams. Send chat messages, post to channels, "
        "or retrieve recent Teams conversations. Use when the user asks to "
        "send a Teams message, notify someone on Teams, or check Teams chats."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "send_message (default) | list_chats",
            },
            "recipient_or_channel": {
                "type": "STRING",
                "description": "Recipient user name/email or channel ID.",
            },
            "message": {
                "type": "STRING",
                "description": "Message content to post on Microsoft Teams.",
            },
            "is_channel": {
                "type": "BOOLEAN",
                "description": "True if posting to a Team channel rather than direct chat.",
            },
            "team_id": {
                "type": "STRING",
                "description": "Optional Team ID if posting to a specific channel.",
            },
            "top": {
                "type": "INTEGER",
                "description": "Number of chats to list (default: 5).",
            },
        },
        "required": ["action"],
    },
    "handler": teams_action,
}
