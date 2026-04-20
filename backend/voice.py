"""
Voice capability status helpers.
"""
from __future__ import annotations

import os
from typing import Dict


def get_voice_status() -> Dict[str, object]:
    return {
        "deepgram": bool(os.getenv("DEEPGRAM_API_KEY")),
        "sarvam": bool(os.getenv("SARVAM_API_KEY")),
        "speaker": "kabir",
        "mode": "push_to_talk",
    }
