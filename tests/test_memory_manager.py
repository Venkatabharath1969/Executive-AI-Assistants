"""
Tests for memory/memory_manager.py
Covers load/save round-trip, update_memory, search_memory, format_memory_for_prompt.
All tests use a tmp_path fixture to avoid touching any real long_term.json.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch


# ── Fixture: redirect MEMORY_PATH to a temp file ────────────────────────────

@pytest.fixture(autouse=True)
def isolated_memory(tmp_path, monkeypatch):
    """Each test gets a fresh empty memory file under tmp_path."""
    import memory.memory_manager as mm
    fake_path = tmp_path / "long_term.json"
    monkeypatch.setattr(mm, "MEMORY_PATH", fake_path)
    yield fake_path


# ── load_memory ───────────────────────────────────────────────────────────────

def test_load_memory_returns_empty_when_no_file():
    from memory.memory_manager import load_memory
    mem = load_memory()
    assert isinstance(mem, dict)
    assert "identity" in mem
    assert "preferences" in mem


def test_load_memory_returns_all_categories():
    from memory.memory_manager import load_memory
    mem = load_memory()
    for cat in ("identity", "preferences", "projects", "relationships", "wishes", "notes"):
        assert cat in mem


# ── update_memory ─────────────────────────────────────────────────────────────

def test_update_memory_persists_a_value(isolated_memory):
    from memory.memory_manager import update_memory, load_memory
    update_memory({"preferences": {"theme": {"value": "dark"}}})
    reloaded = load_memory()
    assert reloaded["preferences"]["theme"]["value"] == "dark"


def test_update_memory_returns_dict(isolated_memory):
    from memory.memory_manager import update_memory
    result = update_memory({"notes": {"test_key": {"value": "hello"}}})
    assert isinstance(result, dict)


def test_update_memory_overwrites_existing_value(isolated_memory):
    from memory.memory_manager import update_memory, load_memory
    update_memory({"preferences": {"lang": {"value": "English"}}})
    update_memory({"preferences": {"lang": {"value": "German"}}})
    mem = load_memory()
    assert mem["preferences"]["lang"]["value"] == "German"


def test_update_memory_noop_on_empty_dict(isolated_memory):
    from memory.memory_manager import update_memory, load_memory
    update_memory({})
    mem = load_memory()
    assert mem["preferences"] == {}


# ── search_memory ─────────────────────────────────────────────────────────────

def test_search_memory_finds_stored_value(isolated_memory):
    from memory.memory_manager import update_memory, search_memory
    update_memory({"relationships": {"bharath_kumar": {"value": "board member and key stakeholder"}}})
    result = search_memory("bharath")
    assert "bharath" in result.lower() or "Bharath" in result


def test_search_memory_returns_nothing_stored_for_unknown(isolated_memory):
    from memory.memory_manager import search_memory
    result = search_memory("xyzzy_not_real")
    assert "nothing" in result.lower() or "not found" in result.lower() or "Nothing" in result


def test_search_memory_empty_query_returns_everything(isolated_memory):
    from memory.memory_manager import update_memory, search_memory
    update_memory({"notes": {"meeting_note": {"value": "discussed EBIT targets"}}})
    result = search_memory("")
    assert "meeting_note" in result.lower() or "ebit" in result.lower()


# ── format_memory_for_prompt ──────────────────────────────────────────────────

def test_format_empty_memory_returns_empty_string(isolated_memory):
    from memory.memory_manager import format_memory_for_prompt
    assert format_memory_for_prompt({}) == ""
    assert format_memory_for_prompt(None) == ""


def test_format_memory_includes_identity(isolated_memory):
    from memory.memory_manager import update_memory, load_memory, format_memory_for_prompt
    update_memory({"identity": {"name": {"value": "Venkata Bharath"}}})
    mem = load_memory()
    result = format_memory_for_prompt(mem)
    assert "Venkata Bharath" in result


def test_format_memory_no_unfilled_placeholders(isolated_memory):
    from memory.memory_manager import update_memory, load_memory, format_memory_for_prompt
    update_memory({"preferences": {"response_style": {"value": "concise bullet points"}}})
    mem = load_memory()
    result = format_memory_for_prompt(mem)
    assert "{" not in result and "}" not in result


def test_format_memory_includes_preferences(isolated_memory):
    from memory.memory_manager import update_memory, load_memory, format_memory_for_prompt
    update_memory({"preferences": {"communication": {"value": "direct and brief"}}})
    mem = load_memory()
    result = format_memory_for_prompt(mem)
    assert "direct and brief" in result
