"""
Context Manager
Handles persistent execution memory for ANAY.
"""
import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

CONTEXT_FILE = "execution_context.json"

class ContextManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContextManager, cls).__new__(cls)
            cls._instance._init_context()
        return cls._instance

    def _init_context(self):
        self.context_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", CONTEXT_FILE))
        if not os.path.exists(self.context_file):
             self._save_context({
                "last_created_file": None,
                "last_opened_file": None,
                "last_modified_file": None,
                "last_opened_app": None,
                "active_project_dir": None,
                "last_task_summary": None,
                "last_content_type": None,
                "last_updated": None
             })

    def get_context(self) -> Dict[str, Any]:
        try:
            with open(self.context_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def update_context(self, updates: Dict[str, Any]):
        """Update specific fields in context."""
        current = self.get_context()
        import datetime
        updates["last_updated"] = datetime.datetime.now().isoformat()
        current.update(updates)
        self._save_context(current)

    def _save_context(self, data: Dict[str, Any]):
        try:
            with open(self.context_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save context: {e}")

    def resolve_path(self, user_ref: str) -> Optional[str]:
        """
        Resolve 'it', 'this', 'that file' to a real path based on priority:
        1. last_modified_file
        2. last_opened_file
        3. last_created_file
        """
        ctx = self.get_context()
        
        # If user explicitly asks for "last created", skip priority
        if "created" in user_ref:
            return ctx.get("last_created_file")
            
        # Default Priority
        return (
            ctx.get("last_modified_file") or 
            ctx.get("last_opened_file") or 
            ctx.get("last_created_file")
        )
