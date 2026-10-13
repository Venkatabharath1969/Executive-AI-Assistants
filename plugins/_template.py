"""
Drop-in Assistant plugin template.

Copy this file, rename it (no leading underscore), fill in PLUGIN and run().
No other file needs to change — discovered automatically at startup.
"""

PLUGIN = {
    "name": "my_plugin",                     # snake_case, unique, ^[a-zA-Z_][a-zA-Z0-9_]{0,63}$
    "description": (
        "One or two sentences Gemini uses to decide when to call this tool. "
        "Be explicit about trigger phrases."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "example_arg": {"type": "STRING", "description": "What this argument means"},
        },
        "required": [],   # omit or leave empty for a zero-argument tool
    },
}

def run(parameters: dict, player=None, session_memory=None) -> str:
    """
    parameters: dict of the args Gemini extracted, matching PLUGIN['parameters'].
    player: the UI instance — use player.write_log(f"NOVA: ...") to log,
            same as actions/*.py. May be None.
    session_memory: reserved.
    Return a short natural-language string — this is spoken back to the user.
    """
    example_arg = parameters.get("example_arg", "")
    try:
        result_text = f"Completed action with {example_arg}."
    except Exception as e:
        return f"Plugin failed: {e}"
    if player:
        try:
            player.write_log(f"NOVA: {result_text}")
        except Exception:
            pass
    return result_text
