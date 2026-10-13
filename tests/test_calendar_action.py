"""
Tests for actions/microsoft_calendar.py
Uses mocked microsoft_client so no real Graph API calls are made.
"""
import json
import pytest
from unittest.mock import MagicMock, patch


def _mock_client(events=None, created=None):
    client = MagicMock()
    client.get_calendar_events.return_value = events or []
    client.create_calendar_event.return_value = created or {"id": "abc123", "status": "created"}
    return client


# ── calendar_action: get_events ───────────────────────────────────────────────

def test_get_events_returns_json_string():
    from actions.microsoft_calendar import calendar_action
    with patch("actions.microsoft_calendar.get_microsoft_client", return_value=_mock_client()):
        result = calendar_action({"action": "get_events"})
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)


def test_get_events_default_action():
    """action key defaults to get_events when omitted."""
    from actions.microsoft_calendar import calendar_action
    mock = _mock_client(events=[{"subject": "1:1 with Bharath Kumar"}])
    with patch("actions.microsoft_calendar.get_microsoft_client", return_value=mock):
        result = calendar_action({})
    mock.get_calendar_events.assert_called_once()
    assert "1:1" in result


def test_get_events_passes_days_ahead():
    from actions.microsoft_calendar import calendar_action
    mock = _mock_client()
    with patch("actions.microsoft_calendar.get_microsoft_client", return_value=mock):
        calendar_action({"action": "get_events", "days_ahead": "7"})
    mock.get_calendar_events.assert_called_once_with(days_ahead=7, top=5)


def test_get_events_passes_top():
    from actions.microsoft_calendar import calendar_action
    mock = _mock_client()
    with patch("actions.microsoft_calendar.get_microsoft_client", return_value=mock):
        calendar_action({"action": "get_events", "top": "10"})
    mock.get_calendar_events.assert_called_once_with(days_ahead=3, top=10)


def test_schedule_alias():
    """'schedule' is a valid alias for get_events."""
    from actions.microsoft_calendar import calendar_action
    mock = _mock_client()
    with patch("actions.microsoft_calendar.get_microsoft_client", return_value=mock):
        result = calendar_action({"action": "schedule"})
    mock.get_calendar_events.assert_called_once()
    assert isinstance(result, str)


# ── calendar_action: create_event ─────────────────────────────────────────────

def test_create_event_success():
    from actions.microsoft_calendar import calendar_action
    mock = _mock_client(created={"id": "evt1", "status": "created"})
    with patch("actions.microsoft_calendar.get_microsoft_client", return_value=mock):
        result = calendar_action({
            "action": "create_event",
            "subject": "Q4 Review",
            "start_time": "2026-10-15T14:00:00",
            "end_time": "2026-10-15T15:00:00",
        })
    assert "created" in result
    mock.create_calendar_event.assert_called_once()


def test_create_event_missing_times_returns_error():
    from actions.microsoft_calendar import calendar_action
    with patch("actions.microsoft_calendar.get_microsoft_client", return_value=_mock_client()):
        result = calendar_action({"action": "create_event", "subject": "Board Meeting"})
    assert "required" in result.lower() or "start_time" in result.lower()


def test_create_event_attendees_string_split():
    from actions.microsoft_calendar import calendar_action
    mock = _mock_client(created={"id": "evt2"})
    with patch("actions.microsoft_calendar.get_microsoft_client", return_value=mock):
        calendar_action({
            "action": "create_event",
            "subject": "Sync",
            "start_time": "2026-10-15T10:00:00",
            "end_time": "2026-10-15T11:00:00",
            "attendees": "a@a.com, b@b.com",
        })
    call_kwargs = mock.create_calendar_event.call_args
    attendees = call_kwargs[1].get("attendees") or call_kwargs[0][3]
    assert len(attendees) == 2


# ── unknown action ────────────────────────────────────────────────────────────

def test_unknown_action_returns_error_string():
    from actions.microsoft_calendar import calendar_action
    with patch("actions.microsoft_calendar.get_microsoft_client", return_value=_mock_client()):
        result = calendar_action({"action": "delete_all_events"})
    assert "unknown" in result.lower() or "supported" in result.lower()


# ── TOOL descriptor ───────────────────────────────────────────────────────────

def test_tool_descriptor_has_required_keys():
    from actions.microsoft_calendar import TOOL
    assert "name" in TOOL
    assert "description" in TOOL
    assert "handler" in TOOL
    assert callable(TOOL["handler"])


def test_tool_descriptor_name():
    from actions.microsoft_calendar import TOOL
    assert TOOL["name"] == "microsoft_calendar"
