# Executive-AI-Assistants

## v2.0 — Luxury CEO UI (feature/luxury-ceo-ui-v2)

### What's New

**AMG Night Edition Color Theme**
The entire UI has been recolored to match a Mercedes-Benz AMG Night Edition executive palette:
- OLED black background: `#070709`
- AMG gold accent: `#C9A84C` (exact AMG badge hex — primary interactive color)
- Platinum secondary: `#B8C2CC`
- All cyan/azure colors replaced; QuantumVisualizer core updated to match.

**SuggestionChips Widget**
After each AI response, 3–4 contextual follow-up suggestion chips appear beneath the conversation log. Chips are generated server-side (no extra LLM call) using a template engine with entity extraction. Click any chip to send it as a voice/text command instantly.

Examples after "What meetings do I have with Bharath?":
- *What was discussed in the previous meeting with Bharath Kumar?*
- *What action items came from the last meeting?*
- *Who else is attending?*
- *Do I have any preparation notes?*

**Agenda Fallback for Board Members**
When a board member's live Microsoft 365 calendar returns empty (e.g. Bharath Kumar visiting from Germany), the assistant automatically falls back to an agenda file in `memory/agendas/`.

To add an agenda file:
1. Place a JSON file in `memory/agendas/` named after the person (lowercase, spaces → underscores):
   - `memory/agendas/bharath_kumar.json`
   - `memory/agendas/sofia_martinez.json`
2. See `memory/agendas/README.md` for the JSON format.
3. A sample agenda for Bharath Kumar is included.

**Test Suite**
```bash
python3 -m pytest tests/ -v
```
Covers: suggestion engine (15+ cases), memory manager, calendar action with agenda fallback.

---