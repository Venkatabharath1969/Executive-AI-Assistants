# Agenda Fallback Files

When a board member's live Microsoft 365 calendar returns no events, NOVA
automatically looks here for an agenda file.

## File naming

Use the person's full name in snake_case:

| Person | File |
|--------|------|
| Bharath Kumar | `bharath_kumar.json` |
| Sarah Johnson | `sarah_johnson.json` |

## Supported formats

- `.json` — structured agenda (preferred)
- `.txt`  — plain text
- `.pdf`  — PDF document
- `.docx` — Word document

## JSON schema

```json
{
  "person": "Full Name",
  "week": "YYYY-WNN",
  "items": [
    {
      "date": "YYYY-MM-DD",
      "time": "HH:MM",
      "title": "Event or meeting title",
      "attendees": ["Name A", "Name B"],
      "notes": "Optional context"
    }
  ]
}
```

## Who qualifies as a board member

Board-member detection uses a keyword list in `actions/microsoft_calendar.py`.
Add names there (`_BOARD_MEMBERS`) before creating their agenda file.
