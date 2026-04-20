"""
Runtime settings shared across chat, voice, and agent execution.
"""
from __future__ import annotations

from typing import Dict


class RuntimeSettings:
    def __init__(self):
        self.default_model = "auto"
        self.offline_mode = False
        self.voice_mode = "push_to_talk"
        self.tts_enabled = False

    def get(self) -> Dict[str, object]:
        return {
            "default_model": self.default_model,
            "offline_mode": self.offline_mode,
            "voice_mode": self.voice_mode,
            "tts_enabled": self.tts_enabled,
        }

    def update(self, patch: Dict[str, object]) -> Dict[str, object]:
        if "default_model" in patch:
            self.default_model = str(patch["default_model"])
        if "offline_mode" in patch:
            self.offline_mode = bool(patch["offline_mode"])
        if "voice_mode" in patch:
            self.voice_mode = str(patch["voice_mode"])
        if "tts_enabled" in patch:
            self.tts_enabled = bool(patch["tts_enabled"])
        return self.get()


runtime_settings = RuntimeSettings()
