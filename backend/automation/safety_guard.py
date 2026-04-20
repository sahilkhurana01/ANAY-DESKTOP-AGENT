"""
Safety Guard Module
Ensures the AI doesn't do anything stupid or dangerous.
"""
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class SafetyGuard:
    """
    Validates actions before execution.
    Acts as a firewall between the AI planner and the OS.
    """
    
    def __init__(self):
        self.dangerous_keywords = [
            "delete", "remove", "rm", "del", "format", 
            "shutdown", "restart", "install", "uninstall", 
            "buy", "pay", "checkout", "transfer"
        ]
        self.critical_paths = [
            "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
            "/bin", "/sbin", "/usr/bin", "/usr/sbin", "/etc"
        ]
        self.safe_mode = True  # Always start in safe mode

    def validate_action(self, tool_name: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if an action is safe to execute.
        Returns: (is_safe, reason/warning_message)
        """
        try:
            # 1. Global Kill Switch check (handled by caller usually, but good to have context)
            
            # 2. File System Checks
            if tool_name == "file_manager":
                action = params.get("action", "")
                path = params.get("path", "")
                
                # Deletion is always high risk
                if action in ["delete", "remove"]:
                    return False, f"⚠️ SAFETY ALERT: Deleting files requires explicit confirmation. Action: {action} on {path}"
                
                # System path protection
                for critical in self.critical_paths:
                    if path and str(path).startswith(critical):
                        return False, f"⛔ BLOCKED: Cannot modify system critical paths: {critical}"

            # 3. System Control Checks
            if tool_name == "system_control":
                command = params.get("command", "")
                
                if any(kw in str(command).lower() for kw in ["shutdown", "restart", "format"]):
                    return False, "⚠️ SAFETY ALERT: System power actions require confirmation."

            # 4. Input/Browser Checks (Payment detection)
            if tool_name in ["browser_agent", "input_controller"]:
                text = str(params).lower()
                if any(kw in text for kw in ["credit card", "cvv", "password", "social security"]):
                    return False, "⛔ BLOCKED: Sensitive data detection. I cannot type passwords or restricted info."
                
                # Payment/Shopping keywords
                if "buy" in text or "checkout" in text:
                    return False, "⚠️ SAFETY ALERT: It looks like you're buying something. Please confirm action."

            return True, "Safe"
            
        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            return False, f"Safety validation error: {e}"

    def ask_confirmation(self, action_description: str) -> str:
        """Helper to format a confirmation request message."""
        return f"✋ WAIT! I need your permission to: {action_description}. Should I proceed? (Yes/No)"
