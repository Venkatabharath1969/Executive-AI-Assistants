"""
microsoft_sharepoint.py — SharePoint & OneDrive Integration Tool.
Search organization documents, team sites, and enterprise cloud files.
"""
from __future__ import annotations

import json
from typing import Any, Dict
from core.microsoft_client import get_microsoft_client

def sharepoint_handler(parameters: dict) -> str:
    """Handle SharePoint and OneDrive search actions."""
    action = parameters.get("action", "search_files").lower()
    client = get_microsoft_client()

    if action in ("search_files", "search", "find_document"):
        query = parameters.get("query", "")
        top = int(parameters.get("limit", 5))
        if not query:
            return "Error: Search query is required."
        res = client.search_sharepoint_files(query=query, top=top)
        return json.dumps(res, indent=2)

    elif action in ("list_sites", "sites"):
        query = parameters.get("query", "")
        res = client.list_sharepoint_sites(query=query)
        return json.dumps(res, indent=2)

    return f"Unsupported SharePoint action '{action}'. Supported actions: 'search_files', 'list_sites'."


TOOL = {
    "name": "microsoft_sharepoint",
    "description": (
        "Search and access enterprise SharePoint sites, team document libraries, and OneDrive files. "
        "Use this tool when the user asks for corporate documents, templates, spreadsheets, or policies on SharePoint."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "Action to perform: 'search_files' (default) or 'list_sites'.",
            },
            "query": {
                "type": "STRING",
                "description": "Keywords or document title to search for on SharePoint.",
            },
            "limit": {
                "type": "INTEGER",
                "description": "Max number of search results to return (default: 5).",
            },
        },
        "required": ["query"],
    },
    "handler": sharepoint_handler,
}
