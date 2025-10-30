# session_state.py

from typing import List
from threading import Lock

# === Shared data containers ===
history: List[dict] = []  # Clicked clickable elements (full metadata)
filtered_actionables: List[dict] = []  # Labeled clickable elements on current screen

# Optional locks (for thread-safe access if needed later)
_history_lock = Lock()
_actionables_lock = Lock()

# === Access methods ===
def get_history_labels(n: int = 20) -> List[str]:
    """Return last N clicked labels (text/desc/class)."""
    with _history_lock:
        return [
            h.get("text") or h.get("desc") or h.get("class", "")
            for h in history[-n:]
            if h.get("text") or h.get("desc") or h.get("class")
        ]

def log_click(clickable: dict):
    """Append a clickable to history."""
    with _history_lock:
        history.append(clickable)

def update_actionables(actionables: List[dict]):
    """Set current screen's labeled clickable elements."""
    with _actionables_lock:
        global filtered_actionables
        filtered_actionables = actionables

def get_actionables() -> List[dict]:
    with _actionables_lock:
        return filtered_actionables.copy()
