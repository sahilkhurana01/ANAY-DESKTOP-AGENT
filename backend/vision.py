"""
Screen capture and optional vision-model analysis.
"""
from __future__ import annotations

import base64
import os
from typing import Any, Dict

from pc_control import take_screenshot

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None


class VisionService:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.available = bool(self.gemini_key and genai)
        if self.available:
            genai.configure(api_key=self.gemini_key)

    def inspect_screen(self, prompt: str = "Describe what is on the screen.") -> Dict[str, Any]:
        screenshot_b64 = take_screenshot()
        result: Dict[str, Any] = {
            "prompt": prompt,
            "screenshot_base64": screenshot_b64,
            "analysis": "Vision model unavailable. Screenshot captured locally.",
            "provider": "local_capture",
        }
        if not self.available:
            return result

        image_bytes = base64.b64decode(screenshot_b64)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(
            [
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes},
            ]
        )
        result["analysis"] = getattr(response, "text", "") or "Vision response received."
        result["provider"] = "gemini"
        return result


vision_service = VisionService()
