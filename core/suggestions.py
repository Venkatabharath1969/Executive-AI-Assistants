"""Template-based follow-up suggestion engine.

Generates 3-4 contextual suggestion chips after each AI response — no LLM call.
Called from main.py's response handler and exposed through NovaUI.show_suggestions().
"""
from __future__ import annotations

import re

_SUGGESTION_TEMPLATES: dict[str, list[str]] = {
    "calendar": [
        "What is this meeting about?",
        "Who else is attending?",
        "Do I have any preparation notes?",
        "What was discussed in the previous meeting with {person}?",
        "What action items came from the last {meeting} meeting?",
    ],
    "email": [
        "Reply to {person}?",
        "Are there other emails from {person}?",
        "Mark this as priority?",
        "What was the context of this thread?",
    ],
    "action_items": [
        "Which action items are overdue?",
        "What did {person} commit to?",
        "Show only critical priority items.",
        "What were the decisions made in that meeting?",
    ],
    "availability": [
        "What is {person}'s agenda for next week?",
        "Can I schedule a meeting with {person}?",
        "What meetings do I have that day?",
        "Find a free slot for {person} and me.",
    ],
    "general": [
        "Tell me more about this.",
        "What should I prioritise today?",
        "Any related action items?",
        "Search for anything about this topic.",
    ],
}

_KNOWN_PEOPLE: list[str] = [
    "Bharath Kumar", "Anupama Singh", "Klaus Weber", "Yuki Tanaka",
    "Marcus Hoffmann", "Elena Petrov", "Heinrich Braun", "Sofia Martinez",
]

# Meeting title regex — matches "- 2026-10-13 14:00 | Board Review" or "- 2026-10-13: Q3 Sync"
_MEETING_RE = re.compile(
    r"- \d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?[^a-zA-Z]*(?::\s*|\s*\|\s*)([^\n(|:]{3,})"
)


class _SafeMap(dict):
    def __missing__(self, key): return ""


def generate(query: str, response: str, history: list[dict]) -> list[str]:
    """Return 3-4 contextual follow-up suggestion strings.

    Args:
        query:    The user's last message.
        response: NOVA's last reply text.
        history:  Recent conversation turns — each a dict with 'query'/'response' keys.
    """
    combined_lower = (query + " " + response).lower()

    if any(w in combined_lower for w in ("meeting", "calendar", "schedule", "agenda", "appointment")):
        intent = "calendar"
    elif any(w in combined_lower for w in ("email", "inbox", "outlook", "message", "mail")):
        intent = "email"
    elif any(w in combined_lower for w in ("action", "task", "todo", "follow-up", "overdue", "commit")):
        intent = "action_items"
    elif any(w in combined_lower for w in ("available", "free", "busy", "availability", "next week")):
        intent = "availability"
    else:
        intent = "general"

    # Extract person from current turn first, then walk back through history
    combined = query + " " + response
    person = ""
    for name in sorted(_KNOWN_PEOPLE, key=len, reverse=True):
        if name.lower() in combined.lower():
            person = name
            break
    if not person:
        for turn in reversed(history[-3:]):
            for name in sorted(_KNOWN_PEOPLE, key=len, reverse=True):
                if name.lower() in (turn.get("query", "") + turn.get("response", "")).lower():
                    person = name
                    break
            if person:
                break

    meeting = ""
    m = _MEETING_RE.search(response)
    if m:
        meeting = m.group(1).strip()

    templates = _SUGGESTION_TEMPLATES.get(intent, _SUGGESTION_TEMPLATES["general"])
    slot_map = _SafeMap(person=person, meeting=meeting)

    suggestions: list[str] = []
    for tmpl in templates:
        filled = tmpl.format_map(slot_map).strip()
        if (filled
                and "{" not in filled
                and "  " not in filled
                and not filled.rstrip().endswith((" with", " from", " by", " for", " about"))):
            suggestions.append(filled)
        if len(suggestions) >= 4:
            break

    # Pad with generics if fewer than 3 filled
    generics = [
        "What should I prioritise today?",
        "Any action items from this?",
        "Tell me more about this.",
        "What meetings do I have today?",
    ]
    for g in generics:
        if len(suggestions) >= 4:
            break
        if g not in suggestions:
            suggestions.append(g)

    return suggestions[:4]
