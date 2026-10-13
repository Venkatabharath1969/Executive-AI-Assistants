"""
viseme.py — Lightweight audio stream scheduler for visualizer sync.
"""
from __future__ import annotations

class VisemeStream:
    """Pass-through stream manager for speech amplitude synchronization."""
    def __init__(self):
        self._current_text = ""

    def reset(self) -> None:
        self._current_text = ""

    def feed_text(self, text: str) -> None:
        self._current_text = str(text or "")

    def frames(self, frames: list, hop: float = 0.02) -> list:
        return frames or []
