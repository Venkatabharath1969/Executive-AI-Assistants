"""
Quantum Neural Core & Energy Visualizer.

A custom software-rendered audio-reactive visualizer with concentric orbital rings,
particle node satellites, glowing energy core, and dynamic frequency pulse ripples.
Built with vector math and QPainter for cross-platform 60 FPS performance without GPU dependencies.
"""
from __future__ import annotations

import math
import random
import time
from typing import Optional

from core.qt_compat import (
    QBrush, QColor, QConicalGradient, QFont, QLinearGradient, QPainter,
    QPainterPath, QPen, QPointF, QPolygonF, QRadialGradient, QRectF,
    QSizePolicy, Qt, QTimer, QWidget,
)


class QuantumVisualizer(QWidget):
    """
    Audio-reactive Quantum Neural Core.
    Replaces static face meshes with an energetic, futuristic animated AI intelligence core.
    """

    def __init__(self, assistant_name: str = "NOVA", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setMinimumSize(320, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._assistant_name = assistant_name
        self.state = "INITIALISING"  # IDLE, LISTENING, THINKING, SPEAKING, SLEEPING, MUTED
        self.muted = False
        self.speaking = False
        self.hud_style = "quantum"
        self._avatar = None

        # Live audio amplitude (0.0 to 1.0)
        self._raw_amp = 0.0
        self._smoothed_amp = 0.0
        self._frequency_bands = [0.0] * 32

        # Animation state & timing
        self._last_time = time.time()
        self._time = 0.0
        self._rotation_angle_1 = 0.0
        self._rotation_angle_2 = 0.0
        self._rotation_angle_3 = 0.0
        self._core_scale = 1.0
        self._pulse_phase = 0.0

        # Colors (cyan / azure cybernetic palette)
        self.col_primary = QColor("#00d4ff")
        self.col_accent = QColor("#00ffb4")
        self.col_deep = QColor("#021b2d")
        self.col_bg = QColor("#000810")
        self.col_glow = QColor(0, 212, 255, 60)
        self.col_warning = QColor("#ff8800")
        self.col_muted = QColor("#ff3366")

        # Orbital particles
        self._particles = []
        for i in range(48):
            self._particles.append({
                "radius": random.uniform(50, 160),
                "angle": random.uniform(0, math.tau),
                "speed": random.uniform(0.3, 1.2) * (1 if random.random() > 0.4 else -1),
                "size": random.uniform(1.5, 3.8),
                "alpha": random.uniform(0.4, 0.9),
                "orbit_idx": random.randint(0, 2),
            })

        # 60 FPS update timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._step)
        self._timer.start(16)

    def set_assistant_name(self, name: str) -> None:
        self._assistant_name = name
        self.update()

    def set_colors(self, primary_hex: str, accent_hex: str = "#00ffb4") -> None:
        try:
            self.col_primary = QColor(primary_hex)
            self.col_glow = QColor(self.col_primary.red(), self.col_primary.green(), self.col_primary.blue(), 50)
            self.col_accent = QColor(accent_hex)
            self.update()
        except Exception:
            pass

    def set_state(self, state: str) -> None:
        self.state = str(state).strip().upper()
        if "SPEAK" in self.state:
            self.speaking = True
        elif "LISTEN" in self.state or "IDLE" in self.state or "SLEEP" in self.state:
            self.speaking = False
        self.update()

    def set_audio_level(self, level: float) -> None:
        """Feed live 0.0–1.0 audio RMS level from microphone or assistant voice."""
        try:
            val = max(0.0, min(1.0, float(level)))
            if val > self._raw_amp:
                self._raw_amp = val
        except Exception:
            pass

    def push_visemes(self, frames, hop: float, at: float) -> None:
        """Compatibility hook: extract amplitude peaks from audio stream."""
        if frames:
            try:
                peak = max(f[0] if isinstance(f, (list, tuple)) else 0.0 for f in frames)
                self.set_audio_level(peak)
            except Exception:
                pass

    def glance(self, dx: float, dy: float, hold: float = 1.0) -> None:
        """Pulse the core slightly on activity."""
        self._core_scale = min(1.4, self._core_scale + 0.15)

    def _step(self) -> None:
        now = time.time()
        dt = max(0.001, min(0.05, now - self._last_time))
        self._last_time = now
        self._time += dt

        # Smooth audio amplitude decay
        self._raw_amp *= 0.88
        self._smoothed_amp += (self._raw_amp - self._smoothed_amp) * 0.35
        amp = self._smoothed_amp

        # Determine state speed multiplier
        speed_mult = 1.0
        if "THINK" in self.state:
            speed_mult = 3.2
        elif "SPEAK" in self.state:
            speed_mult = 1.8 + amp * 2.0
        elif "LISTEN" in self.state:
            speed_mult = 1.2 + amp * 1.5
        elif self.muted:
            speed_mult = 0.4

        # Rotate orbital rings
        self._rotation_angle_1 = (self._rotation_angle_1 + dt * 0.8 * speed_mult) % math.tau
        self._rotation_angle_2 = (self._rotation_angle_2 - dt * 1.1 * speed_mult) % math.tau
        self._rotation_angle_3 = (self._rotation_angle_3 + dt * 0.5 * speed_mult) % math.tau

        # Pulse phase for breathing
        self._pulse_phase += dt * (2.5 if "THINK" in self.state else 1.2)

        # Update frequency bands
        base_h = 10.0 + amp * 60.0
        for i in range(len(self._frequency_bands)):
            harmonic = math.sin(self._time * 6.0 + i * 0.4) * 0.5 + 0.5
            target_h = base_h * (0.3 + 0.7 * harmonic) * (1.0 - 0.4 * abs(i - 16) / 16.0)
            self._frequency_bands[i] += (target_h - self._frequency_bands[i]) * 0.25

        # Update particles
        for p in self._particles:
            p["angle"] = (p["angle"] + dt * p["speed"] * speed_mult) % math.tau

        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0
        dim = min(w, h)
        scale = dim / 440.0

        # Background fill
        painter.fillRect(0, 0, w, h, self.col_bg)

        # Ambient background grid dots
        painter.setPen(QPen(QColor(0, 212, 255, 18), 1))
        step_grid = 36
        for gx in range(0, w, step_grid):
            for gy in range(0, h, step_grid):
                painter.drawPoint(gx, gy)

        amp = self._smoothed_amp
        is_listening = "LISTEN" in self.state
        is_speaking = "SPEAK" in self.state or self.speaking
        is_thinking = "THINK" in self.state
        is_muted = self.muted or "MUTE" in self.state

        # Primary palette choice for current state
        if is_muted:
            main_col = self.col_muted
            sec_col = QColor("#ff6688")
        elif is_thinking:
            main_col = QColor("#ffaa00")
            sec_col = QColor("#00e5ff")
        elif is_speaking:
            main_col = self.col_accent
            sec_col = self.col_primary
        elif is_listening:
            main_col = self.col_primary
            sec_col = self.col_accent
        else:
            main_col = self.col_primary
            sec_col = QColor("#00a2cc")

        # ── 1. Outer Ambient Aura / Glow Bloom ─────────────────────────────────
        aura_rad = (150 + 40 * amp + 10 * math.sin(self._pulse_phase)) * scale
        aura_grad = QRadialGradient(cx, cy, aura_rad)
        aura_grad.setColorAt(0.0, QColor(main_col.red(), main_col.green(), main_col.blue(), int(65 + 60 * amp)))
        aura_grad.setColorAt(0.5, QColor(sec_col.red(), sec_col.green(), sec_col.blue(), int(25 + 25 * amp)))
        aura_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(aura_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), aura_rad, aura_rad)

        # ── 2. Radial Frequency Bars ──────────────────────────────────────────
        num_bars = len(self._frequency_bands)
        bar_base_r = 120 * scale
        painter.save()
        painter.translate(cx, cy)
        for i in range(num_bars):
            angle = (i / num_bars) * math.tau + self._rotation_angle_3 * 0.4
            bar_len = (self._frequency_bands[i] + 4) * scale
            x1 = math.cos(angle) * bar_base_r
            y1 = math.sin(angle) * bar_base_r
            x2 = math.cos(angle) * (bar_base_r + bar_len)
            y2 = math.sin(angle) * (bar_base_r + bar_len)

            bar_alpha = int(90 + min(150, self._frequency_bands[i] * 3.5))
            bar_pen = QPen(QColor(sec_col.red(), sec_col.green(), sec_col.blue(), bar_alpha), 2.2 * scale)
            bar_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(bar_pen)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        painter.restore()

        # ── 3. Outer Concentric Orbital Quantum Ring (Segmented) ───────────────
        painter.save()
        painter.translate(cx, cy)
        ring1_r = 108 * scale
        ring1_pen = QPen(QColor(main_col.red(), main_col.green(), main_col.blue(), 140), 1.6 * scale)
        ring1_pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(ring1_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.rotate(math.degrees(self._rotation_angle_1))
        painter.drawEllipse(QPointF(0, 0), ring1_r, ring1_r)

        # Ring tick markers
        tick_pen = QPen(QColor(main_col.red(), main_col.green(), main_col.blue(), 180), 1.2 * scale)
        painter.setPen(tick_pen)
        for a_deg in range(0, 360, 30):
            rad = math.radians(a_deg)
            tx1 = math.cos(rad) * (ring1_r - 5 * scale)
            ty1 = math.sin(rad) * (ring1_r - 5 * scale)
            tx2 = math.cos(rad) * (ring1_r + 5 * scale)
            ty2 = math.sin(rad) * (ring1_r + 5 * scale)
            painter.drawLine(QPointF(tx1, ty1), QPointF(tx2, ty2))
        painter.restore()

        # ── 4. Middle Elliptical Orbital Ring (Tilted 3D Effect) ───────────────
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(self._rotation_angle_2))
        ring2_rx = (88 + 12 * amp) * scale
        ring2_ry = (54 + 8 * amp) * scale
        ring2_pen = QPen(QColor(sec_col.red(), sec_col.green(), sec_col.blue(), 160), 1.8 * scale)
        painter.setPen(ring2_pen)
        painter.drawEllipse(QPointF(0, 0), ring2_rx, ring2_ry)
        painter.restore()

        # ── 5. Inner Resonance Ring ───────────────────────────────────────────
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(self._rotation_angle_3))
        ring3_r = (64 + 18 * amp) * scale
        ring3_pen = QPen(QColor(main_col.red(), main_col.green(), main_col.blue(), 210), 2.2 * scale)
        painter.setPen(ring3_pen)
        painter.drawEllipse(QPointF(0, 0), ring3_r, ring3_r)
        painter.restore()

        # ── 6. Floating Orbital Node Particles ────────────────────────────────
        painter.save()
        painter.translate(cx, cy)
        for p in self._particles:
            pr = p["radius"] * scale * (1.0 + 0.2 * amp)
            px = math.cos(p["angle"]) * pr
            py = math.sin(p["angle"]) * pr
            ps = p["size"] * scale * (1.0 + 0.4 * amp)
            p_alpha = int(p["alpha"] * (180 + 75 * amp))
            painter.setBrush(QBrush(QColor(sec_col.red(), sec_col.green(), sec_col.blue(), p_alpha)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(px, py), ps, ps)
        painter.restore()

        # ── 7. Central Fusion Core (Multi-gradient Energy Sphere) ─────────────
        core_r = (32 + 14 * amp + 3 * math.sin(self._pulse_phase * 2)) * scale
        core_grad = QRadialGradient(cx, cy, core_r)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 245))
        core_grad.setColorAt(0.35, QColor(main_col.red(), main_col.green(), main_col.blue(), 220))
        core_grad.setColorAt(0.75, QColor(sec_col.red(), sec_col.green(), sec_col.blue(), 150))
        core_grad.setColorAt(1.0, QColor(main_col.red(), main_col.green(), main_col.blue(), 0))

        painter.setBrush(QBrush(core_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), core_r, core_r)

        # ── 8. Status Badge & Hologram Text ───────────────────────────────────
        painter.setFont(QFont("Courier New", int(max(9, 11 * scale)), QFont.Weight.Bold))
        text_col = QColor(main_col.red(), main_col.green(), main_col.blue(), 220)
        painter.setPen(text_col)

        # Assistant Name at Core Center
        name_text = self._assistant_name.upper()
        name_rect = QRectF(cx - 100 * scale, cy - 10 * scale, 200 * scale, 20 * scale)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, name_text)

        # State indicator pill below core
        pill_w = 140 * scale
        pill_h = 24 * scale
        pill_y = cy + 128 * scale
        pill_rect = QRectF(cx - pill_w / 2, pill_y, pill_w, pill_h)

        pill_bg = QColor(main_col.red(), main_col.green(), main_col.blue(), 30)
        pill_border = QColor(main_col.red(), main_col.green(), main_col.blue(), 130)
        painter.setBrush(QBrush(pill_bg))
        painter.setPen(QPen(pill_border, 1.2))
        painter.drawRoundedRect(pill_rect, 4.0, 4.0)

        status_label = f"◈ {self.state} ◈"
        painter.setFont(QFont("Courier New", int(max(8, 9 * scale)), QFont.Weight.Bold))
        painter.setPen(main_col)
        painter.drawText(pill_rect, Qt.AlignmentFlag.AlignCenter, status_label)
