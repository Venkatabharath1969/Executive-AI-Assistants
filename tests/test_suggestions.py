"""
Comprehensive tests for the NOVA suggestion engine.
Tests intent detection, entity extraction, template filling, and edge cases.
"""
import pytest
from tests.conftest import _generate_suggestions, _KNOWN_PEOPLE


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sugg(query="", response="", history=None):
    return _generate_suggestions(query, response, history or [])


# ── Basic contract ────────────────────────────────────────────────────────────

def test_returns_list():
    result = _sugg("What meetings do I have today?")
    assert isinstance(result, list)


def test_all_items_are_strings():
    result = _sugg("What meetings do I have today?")
    assert all(isinstance(s, str) for s in result)


def test_max_4_suggestions():
    result = _sugg("Tell me everything about Bharath Kumar's schedule and emails and tasks and availability")
    assert len(result) <= 4


def test_at_least_1_suggestion():
    result = _sugg("What meetings do I have today?")
    assert len(result) >= 1


# ── Intent detection ─────────────────────────────────────────────────────────

def test_calendar_intent_meeting_keyword():
    result = _sugg("What meetings do I have today?")
    calendar_suggestions = {"What is this meeting about?", "Who else is attending?",
                             "Do I have any preparation notes?", "What meetings do I have today?"}
    assert any(s in calendar_suggestions for s in result)


def test_calendar_intent_schedule_keyword():
    result = _sugg("Show me my schedule for this week")
    calendar_suggestions = {"What is this meeting about?", "Who else is attending?",
                             "Do I have any preparation notes?", "What meetings do I have today?"}
    assert any(s in calendar_suggestions for s in result)


def test_calendar_intent_agenda_keyword():
    result = _sugg("What is on my agenda today?")
    calendar_suggestions = {"What is this meeting about?", "Who else is attending?",
                             "Do I have any preparation notes?", "What meetings do I have today?"}
    assert any(s in calendar_suggestions for s in result)


def test_email_intent_inbox_keyword():
    result = _sugg("Check my inbox")
    email_suggestions = {"Mark this as priority?", "What was the context of this thread?"}
    assert any(s in email_suggestions for s in result)


def test_email_intent_email_keyword():
    result = _sugg("Do I have any emails?")
    email_suggestions = {"Mark this as priority?", "What was the context of this thread?"}
    assert any(s in email_suggestions for s in result)


def test_action_items_overdue_keyword():
    result = _sugg("What are my overdue action items?")
    assert "Which action items are overdue?" in result


def test_action_items_commit_keyword():
    result = _sugg("What did Marcus Hoffmann commit to?", response="Marcus Hoffmann committed to reviewing the risk matrix.")
    assert any("Marcus Hoffmann" in s for s in result)


def test_availability_intent():
    result = _sugg("Is Bharath available next week?")
    avail_suggestions = {
        "What is Bharath Kumar's agenda for next week?",
        "Can I schedule a meeting with Bharath Kumar?",
        "What meetings do I have that day?",
        "Find a free slot for Bharath Kumar and me.",
    }
    assert any(s in avail_suggestions for s in result)


def test_general_intent_fallback():
    result = _sugg("What is the capital of France?")
    assert "Tell me more about this." in result or "What should I prioritise today?" in result


# ── Entity extraction ─────────────────────────────────────────────────────────

def test_person_entity_bharath_kumar():
    result = _sugg("Tell me about the 1:1 with Bharath Kumar")
    assert any("Bharath Kumar" in s for s in result)


def test_person_entity_in_response():
    result = _sugg("What happened in the last meeting?",
                   response="The meeting with Elena Petrov covered the CSRD scope.")
    assert any("Elena Petrov" in s for s in result)


def test_longer_name_preferred():
    """'Bharath Kumar' should be matched over a hypothetical shorter 'Bharath'."""
    result = _sugg("What did Bharath Kumar say about the budget?")
    # Should have "Bharath Kumar" not just "Bharath"
    person_suggestions = [s for s in result if "Bharath" in s]
    for s in person_suggestions:
        assert "Bharath Kumar" in s, f"Partial name in suggestion: {s!r}"


def test_session_history_entity_fallback():
    """If current query has no entity, inherit from session history."""
    history = [
        {"query": "Tell me about Bharath Kumar's schedule", "response": "Meeting on Monday."},
    ]
    result = _sugg("What did they say about the budget?", history=history)
    assert any("Bharath Kumar" in s for s in result)


# ── Template quality ──────────────────────────────────────────────────────────

def test_no_unfilled_placeholders():
    """No {curly} braces should appear in any output suggestion."""
    for intent_kw in ["meeting", "inbox", "overdue", "available next week", "random query xyz"]:
        result = _sugg(intent_kw)
        for s in result:
            assert "{" not in s and "}" not in s, f"Unfilled placeholder in: {s!r}"


def test_no_double_spaces():
    """Suggestions must not contain double spaces (from empty entity slots)."""
    result = _sugg("What are my meetings?", response="", history=[])
    for s in result:
        assert "  " not in s, f"Double-space in suggestion: {s!r}"


def test_no_trailing_prepositions():
    """Suggestions ending in 'with', 'from', 'by', 'for', 'about' are invalid."""
    bad_endings = (" with", " from", " by", " for", " about")
    for q in ["Tell me about the meeting with", "What did they discuss", ""]:
        result = _sugg(q)
        for s in result:
            assert not any(s.rstrip().endswith(e) for e in bad_endings), \
                f"Trailing preposition in: {s!r}"


def test_generics_padded_when_no_entity():
    """When no entity is found and all templates have slots, generics fill the gap."""
    result = _sugg("some query with no known person", response="")
    generics = {"What should I prioritise today?", "Any action items from this?",
                "Tell me more about this.", "What meetings do I have today?"}
    assert any(s in generics for s in result), f"No generic fallback in: {result}"


# ── Robustness ────────────────────────────────────────────────────────────────

def test_empty_query_and_response_does_not_crash():
    result = _sugg("", "")
    assert isinstance(result, list)


def test_empty_history_does_not_crash():
    result = _sugg("What is my schedule?", history=[])
    assert isinstance(result, list)


def test_all_intents_return_non_empty():
    """Every intent branch must produce at least one suggestion."""
    cases = [
        ("What meetings do I have?", "calendar"),
        ("Check my inbox", "email"),
        ("What are my overdue tasks?", "action_items"),
        ("Is Klaus Weber available?", "availability"),
        ("Random question xyz", "general"),
    ]
    for query, _ in cases:
        result = _sugg(query)
        assert len(result) >= 1, f"Empty suggestions for query: {query!r}"


def test_meeting_title_extracted_from_response():
    """Meeting title from formatted response should appear in a suggestion."""
    response = "- 2026-10-15 14:00: Q4 Budget Review | Bharath Kumar presented EBIT."
    result = _sugg("What happened in the last meeting?", response=response)
    meeting_suggestions = [s for s in result if "Q4 Budget Review" in s]
    assert len(meeting_suggestions) >= 1, f"Meeting title not in suggestions: {result}"
