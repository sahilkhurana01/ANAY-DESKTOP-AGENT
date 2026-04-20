"""
Wake word capability wrapper.
"""
from __future__ import annotations

import os
from typing import Dict

try:
    import pvporcupine
except Exception:  # pragma: no cover
    pvporcupine = None


def get_wake_word_status() -> Dict[str, object]:
    key_present = bool(os.getenv("PICOVOICE_ACCESS_KEY"))
    return {
        "enabled": key_present and pvporcupine is not None,
        "engine": "pvporcupine" if pvporcupine else "unavailable",
        "wake_phrase": "Hey ANAY",
    }
