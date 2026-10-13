"""
send_message.py — Clean, direct messaging tool.
Sends messages via Webhook, Email, or Microsoft Teams without controlling the PC mouse or keyboard.
"""
from __future__ import annotations

import json
import os
import requests
from typing import Optional
from core.microsoft_client import get_microsoft_client

def send_message_handler(parameters: dict) -> str:
    channel = parameters.get("channel", "teams").lower()
    recipient = parameters.get("recipient", "")
    message = parameters.get("message", "")

    if not message:
        return "Error: Message content is required."

    if channel in ("teams", "microsoft_teams"):
        client = get_microsoft_client()
        res = client.send_teams_message(recipient or "general", message)
        return json.dumps(res, indent=2)

    elif channel in ("email", "outlook"):
        client = get_microsoft_client()
        subject = parameters.get("subject", "Notification from AI Assistant")
        res = client.send_outlook_email(to_recipients=recipient or "user@enterprise.com", subject=subject, body=message)
        return json.dumps(res, indent=2)

    elif channel == "webhook":
        url = parameters.get("webhook_url") or os.getenv("NOTIFICATION_WEBHOOK_URL")
        if not url:
            return "Error: Webhook URL is required for webhook notifications."
        try:
            resp = requests.post(url, json={"recipient": recipient, "message": message}, timeout=10)
            return f"Webhook message dispatched. Status: {resp.status_code}"
        except Exception as e:
            return f"Error sending webhook: {e}"

    return f"Unsupported messaging channel '{channel}'. Supported channels: teams, email, webhook."


TOOL = {
    "name": "send_message",
    "description": (
        "Send a message or notification to a contact, team channel, or webhook. "
        "Channels supported: 'teams', 'email', 'webhook'. "
        "Does NOT control your local screen or mouse."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "channel": {
                "type": "STRING",
                "description": "Destination channel: 'teams' (default), 'email', or 'webhook'.",
            },
            "recipient": {
                "type": "STRING",
                "description": "Recipient name, email address, or channel name.",
            },
            "message": {
                "type": "STRING",
                "description": "Text content of the message.",
            },
            "subject": {
                "type": "STRING",
                "description": "Optional email subject (if channel is email).",
            },
            "webhook_url": {
                "type": "STRING",
                "description": "Optional webhook endpoint URL (if channel is webhook).",
            },
        },
        "required": ["message"],
    },
    "handler": send_message_handler,
}
