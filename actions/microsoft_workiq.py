"""
WorkIQ MCP & Microsoft 365 Enterprise Knowledge Search Tool.
Connects with the WorkIQ MCP server / Graph Copilot context.
"""
from __future__ import annotations
import json
from core.microsoft_client import get_microsoft_client

def workiq_action(parameters: dict) -> str:
    """Execute enterprise search across Microsoft 365 using WorkIQ."""
    query = parameters.get("query", "")
    scope = parameters.get("scope", "all")
    max_results = int(parameters.get("max_results", 4))

    if not query:
        return "Please provide a query to search WorkIQ / enterprise Microsoft 365."

    client = get_microsoft_client()
    result = client.query_workiq(query=query, scope=scope, max_results=max_results)
    return json.dumps(result, indent=2)


TOOL = {
    "name": "workiq_search",
    "description": (
        "Enterprise intelligence search via WorkIQ / Microsoft Graph. Searches across "
        "Teams discussions, emails, OneDrive files, and company documentation. "
        "Use when user asks about internal enterprise topics, past decisions, "
        "team discussions, or corporate documents."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "Enterprise search query or question.",
            },
            "scope": {
                "type": "STRING",
                "description": "all | teams | outlook | onedrive | sharepoint",
            },
            "max_results": {
                "type": "INTEGER",
                "description": "Maximum number of enterprise references to retrieve.",
            },
        },
        "required": ["query"],
    },
    "handler": workiq_action,
}
