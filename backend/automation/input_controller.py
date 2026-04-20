"""
Input Controller Module
Wrapper around pyautogui and keyboard/mouse libraries for simulated human input.
"""
import logging
import time
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class InputController:
    """Controls Mouse and Keyboard actions."""
    
    def __init__(self):
        try:
            import pyautogui
            # Fail-safe: moving mouse to corner throws exception
            pyautogui.FAILSAFE = True
            # Small delay for visual feedback
            pyautogui.PAUSE = 0.5 
            self.pyautogui = pyautogui
            self.has_gui = True
        except ImportError:
            logger.error("PyAutoGUI not installed. Input automation disabled.")
            self.has_gui = False

    def move_mouse(self, x: int, y: int, duration: float = 0.5):
        """Move mouse to coordinates."""
        if not self.has_gui: return False
        try:
            self.pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"Mouse move failed: {e}")
            return False

    def click(self, x: Optional[int] = None, y: Optional[int] = None, clicks: int = 1, button: str = 'left'):
        """Click mouse."""
        if not self.has_gui: return False
        try:
            self.pyautogui.click(x=x, y=y, clicks=clicks, button=button)
            return True
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False

    def type_text(self, text: str, interval: float = 0.2):
        """Type text like a human."""
        if not self.has_gui: return False
        try:
            # Short pause to ensure focus is settled
            time.sleep(0.5)
            self.pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            logger.error(f"Typing failed: {e}")
            return False

    def press_key(self, key: str):
        """Press a single key (e.g., 'enter', 'esc')."""
        if not self.has_gui: return False
        try:
            self.pyautogui.press(key)
            return True
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            return False

    def hotkey(self, keys):
        """Press a combination (e.g., ['ctrl', 'c'])."""
        if not self.has_gui: return False
        try:
            # Handle both list and varargs if needed, but primarily list from JSON
            if isinstance(keys, str):
                params = [keys]
            else:
                params = keys
            
            self.pyautogui.hotkey(*params)
            return True
        except Exception as e:
            logger.error(f"Hotkey failed: {e}")
            return False

    def scroll(self, amount: int):
        """Scroll up (positive) or down (negative)."""
        if not self.has_gui: return False
        try:
            self.pyautogui.scroll(amount)
            return True
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False
            
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        if not self.has_gui: return (0, 0)
        return self.pyautogui.position()

    def media_play_pause(self):
        """Toggle Media Play/Pause."""
        return self.press_key("playpause")

    def media_next(self):
        """Next Track."""
        return self.press_key("nexttrack")

    def media_prev(self):
        """Previous Track."""
        return self.press_key("prevtrack")

    def volume_up(self):
        """Volume Up."""
        return self.press_key("volumeup")

    def volume_down(self):
        """Volume Down."""
        return self.press_key("volumedown")

    def wait(self, seconds: float):
        """Wait for UI to load."""
        time.sleep(seconds)
        return True
