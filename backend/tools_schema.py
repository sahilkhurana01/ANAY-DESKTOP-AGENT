"""
Tool schemas exposed to LLMs and frontend settings panels.
"""
from __future__ import annotations

from typing import Any, Dict, List


TOOLS: List[Dict[str, Any]] = [
    {
        "name": "open_app",
        "description": "Open a local desktop application by common name.",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "name": "close_app",
        "description": "Close or kill a local application by process name.",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "name": "type_text",
        "description": "Type text into the currently focused application.",
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "take_screenshot",
        "description": "Capture the full desktop and return it as base64 JPEG.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "read_clipboard",
        "description": "Read current clipboard text.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "write_clipboard",
        "description": "Write text to the system clipboard.",
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "run_terminal_command",
        "description": "Run a shell command locally and return stdout/stderr.",
        "parameters": {
            "type": "object",
            "properties": {"cmd": {"type": "string"}},
            "required": ["cmd"],
        },
    },
    {
        "name": "open_url",
        "description": "Open a URL in the default browser.",
        "parameters": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "search_web",
        "description": "Search the web and return starter results.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "get_system_stats",
        "description": "Get local CPU, RAM, disk and battery info.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "list_running_apps",
        "description": "List running local applications and processes.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "list_apps",
        "description": "List names of running applications (short list for quick context).",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "focus_window",
        "description": "Focus the first window that matches a title fragment (e.g. Chrome, Spotify, YouTube).",
        "parameters": {
            "type": "object",
            "properties": {"title": {"type": "string"}},
            "required": ["title"],
        },
    },
    {
        "name": "scroll",
        "description": "Scroll the mouse wheel up or down.",
        "parameters": {
            "type": "object",
            "properties": {
                "direction": {"type": "string", "enum": ["up", "down"]},
                "amount": {"type": "integer"},
            },
            "required": ["direction"],
        },
    },
    {
        "name": "click_at",
        "description": "Click at screen coordinates.",
        "parameters": {
            "type": "object",
            "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
            "required": ["x", "y"],
        },
    },
    {
        "name": "move_file",
        "description": "Move a file from one path to another path.",
        "parameters": {
            "type": "object",
            "properties": {
                "src": {"type": "string"},
                "dest": {"type": "string"},
            },
            "required": ["src", "dest"],
        },
    },
    {
        "name": "delete_file",
        "description": "Delete a file or folder. Use only after confirmation for important paths.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "read_file",
        "description": "Read UTF-8 text content from a file.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write UTF-8 text content to a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "play_media",
        "description": "Start media playback by searching for a song, playlist, or video.",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "name": "send_email",
        "description": "Send an email through configured SMTP credentials.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to", "subject", "body"],
        },
    },
    {
        "name": "send_whatsapp",
        "description": "Send a WhatsApp message by phone number or contact name (e.g. 'Vansh').",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "Phone number (with/without country code) OR contact name"},
                "message": {"type": "string", "description": "Message content"},
            },
            "required": ["recipient", "message"],
        },
    },
    {
        "name": "set_reminder",
        "description": "Create a local reminder for a future ISO timestamp.",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "time": {"type": "string"},
            },
            "required": ["task", "time"],
        },
    },
    {
        "name": "set_volume",
        "description": "Set master output volume from 0 to 100.",
        "parameters": {
            "type": "object",
            "properties": {"level": {"type": "integer"}},
            "required": ["level"],
        },
    },
    {
        "name": "volume_up",
        "description": "Increase volume by amount (default 10).",
        "parameters": {
            "type": "object",
            "properties": {"amount": {"type": "integer", "default": 10}},
        },
    },
    {
        "name": "volume_down",
        "description": "Decrease volume by amount (default 10).",
        "parameters": {
            "type": "object",
            "properties": {"amount": {"type": "integer", "default": 10}},
        },
    },
    {
        "name": "mute_volume",
        "description": "Mute or unmute the system volume.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_volume",
        "description": "Get the current system volume level.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "bluetooth_on",
        "description": "Turn Bluetooth ON.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "bluetooth_off",
        "description": "Turn Bluetooth OFF.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "bluetooth_status",
        "description": "Check if Bluetooth is on or off.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "wifi_on",
        "description": "Turn WiFi ON.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "wifi_off",
        "description": "Turn WiFi OFF.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "set_brightness",
        "description": "Set screen brightness from 0 to 100.",
        "parameters": {
            "type": "object",
            "properties": {"level": {"type": "integer"}},
            "required": ["level"],
        },
    },
    {
        "name": "night_mode_on",
        "description": "Open Night Mode / Night Light settings.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "lock_screen",
        "description": "Lock the current desktop session.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "open_youtube",
        "description": "Open YouTube in the default browser.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "play_youtube_automated",
        "description": "Search and play a song automatically on YouTube using simulated GUI automation.",
        "parameters": {
            "type": "object",
            "properties": {"song_name": {"type": "string"}},
            "required": ["song_name"],
        },
    },
    {
        "name": "click_mouse",
        "description": "Click the mouse at specific screen coordinates (x, y).",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "clicks": {"type": "integer", "default": 1},
            },
            "required": ["x", "y"],
        },
    },
    {
        "name": "move_mouse",
        "description": "Move the mouse cursor to specific screen coordinates (x, y).",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
            },
            "required": ["x", "y"],
        },
    },
    {
        "name": "scroll_mouse",
        "description": "Scroll the mouse wheel.",
        "parameters": {
            "type": "object",
            "properties": {"amount": {"type": "integer", "description": "Positive to scroll up, negative to scroll down."}},
            "required": ["amount"],
        },
    },
    {
        "name": "shutdown",
        "description": "Shut down the computer. Use only after confirmation.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "restart",
        "description": "Restart the computer. Use only after confirmation.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "save_user_fact",
        "description": "Explicitly save a fact about the user (e.g. name, age, city, favorite thing).",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Short key name e.g. 'naam', 'city'"},
                "value": {"type": "string", "description": "The fact value being saved"}
            },
            "required": ["key", "value"]
        }
    },
    {
        "name": "save_important_memory",
        "description": "Save an important long-term memory that doesn't fit a simple fact key.",
        "parameters": {
            "type": "object",
            "properties": {
                "memory": {"type": "string", "description": "The memory text to save"}
            },
            "required": ["memory"]
        }
    },
    {
        "name": "save_contact",
        "description": "Explicitly save or update a contact's phone number in the database.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the person (e.g. 'Vansh')"},
                "phone": {"type": "string", "description": "Phone number with country code (e.g. '919876543210')"}
            },
            "required": ["name", "phone"]
        }
    }
]
