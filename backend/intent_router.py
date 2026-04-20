"""
High-confidence local intents: run tools without waiting for the LLM.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from pc_control import execute_tool

_LAUNCH_VERB = re.compile(
    r"\b(open|launch|start|visit|go to|take me to|show me|play|search)\b",
    re.IGNORECASE,
)


def _log(name: str, arguments: Dict[str, Any], result: Any) -> Dict[str, Any]:
    return {"name": name, "arguments": arguments, "result": result}


def try_handle_command(prompt: str) -> Optional[Tuple[str, List[Dict[str, Any]]]]:
    """
    Returns (assistant_text, tool_calls_executed) when a deterministic intent ran.
    """
    raw = (prompt or "").strip()
    if not raw:
        return None
    msg = raw.lower()

    # Explicit URL in message
    url_in_text = re.search(r"https?://[^\s]+", raw, re.IGNORECASE)
    if url_in_text and _LAUNCH_VERB.search(msg):
        url = url_in_text.group(0).rstrip(").,]")
        result = execute_tool("open_url", {"url": url})
        text = str(result) if not isinstance(result, str) else result
        return text, [_log("open_url", {"url": url}, result)]

    if not _LAUNCH_VERB.search(msg):
        return None

    # YouTube (site or app wording)
    if re.search(r"\byoutube\b", msg) and not re.search(r"youtube\.com|youtu\.be", msg):
        if re.search(r"\b(play|search)\b", msg):
            cleaned = re.sub(
                r"(?i)^.*?\b(play|search)\b",
                "",
                raw,
                count=1,
            ).strip()
            cleaned = re.sub(r"(?i)\bon\s+youtube\b.*$", "", cleaned).strip()
            cleaned = re.sub(r"(?i)\byoutube\b", "", cleaned).strip()
            if len(cleaned) >= 2:
                result = execute_tool("play_youtube_automated", {"song_name": cleaned})
                text = str(result) if isinstance(result, str) else str(result)
                return text, [_log("play_youtube_automated", {"song_name": cleaned}, result)]
        result = execute_tool("open_youtube", {})
        text = str(result) if isinstance(result, str) else str(result)
        return text, [_log("open_youtube", {}, result)]

    # google.com shortcut
    if re.search(r"\bgoogle\b", msg) and "youtube" not in msg:
        result = execute_tool("open_url", {"url": "https://www.google.com"})
        text = str(result) if isinstance(result, str) else str(result)
        return text, [_log("open_url", {"url": "https://www.google.com"}, result)]

    # Map spoken app names → open_app name token
    app_patterns: List[Tuple[re.Pattern[str], str]] = [
        (re.compile(r"\bchrome\b|\bgoogle chrome\b", re.I), "chrome"),
        (re.compile(r"\bbrave\b", re.I), "brave"),
        (re.compile(r"\bfirefox\b", re.I), "firefox"),
        (re.compile(r"\bedge\b|\bmicrosoft edge\b", re.I), "edge"),
        (re.compile(r"\bspotify\b", re.I), "spotify"),
        (re.compile(r"\bnotepad\b", re.I), "notepad"),
        (re.compile(r"\bcalculator\b|\bcalc\b", re.I), "calculator"),
        (re.compile(r"\bdiscord\b", re.I), "discord"),
        (re.compile(r"\btelegram\b", re.I), "telegram"),
        (re.compile(r"\bwhatsapp\b", re.I), "whatsapp"),
        (re.compile(r"\bvlc\b", re.I), "vlc"),
        (re.compile(r"\bcode\b|\bvscode\b|\bvs code\b", re.I), "vscode"),
        (re.compile(r"\bcmd\b|\bcommand prompt\b", re.I), "cmd"),
        (re.compile(r"\bpowershell\b", re.I), "powershell"),
        (re.compile(r"\bexplorer\b|\bfile explorer\b", re.I), "explorer"),
        (re.compile(r"\bpaint\b", re.I), "paint"),
        (re.compile(r"\bword\b", re.I), "word"),
        (re.compile(r"\bexcel\b", re.I), "excel"),
    ]
    for pattern, app_key in app_patterns:
        if pattern.search(msg):
            result = execute_tool("open_app", {"name": app_key})
            text = str(result) if isinstance(result, str) else str(result)
            return text, [_log("open_app", {"name": app_key}, result)]

    return None
