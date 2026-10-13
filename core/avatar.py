"""
Avatar & Visualizer interface.
Connects the UI to our custom Quantum Neural Core visualizer.
"""
from __future__ import annotations

from core.visualizer import QuantumVisualizer

class HoloAvatar:
    """
    Adapter providing compatibility for the visualizer.
    Directs audio events and states to the Quantum Visualizer.
    """
    def __init__(self):
        self.state = "IDLE"
        self.speaking = False
        self.muted = False

    def step(self, dt: float, amp: float, speaking: bool = False,
             muted: bool = False, state: str = "IDLE", **kwargs) -> None:
        self.speaking = speaking
        self.muted = muted
        self.state = state

    def glance(self, dx: float, dy: float, hold: float = 1.1) -> None:
        pass
