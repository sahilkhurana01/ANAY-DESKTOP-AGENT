import pyautogui
import time
import logging

logger = logging.getLogger(__name__)

# Basic settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

def click(x: int, y: int):
    """Click at specific coordinates"""
    pyautogui.click(x, y)
    return f"Clicked at {x}, {y}"

def double_click(x: int, y: int):
    """Double click at specific coordinates"""
    pyautogui.doubleClick(x, y)
    return f"Double clicked at {x}, {y}"

def right_click(x: int, y: int):
    """Right click at specific coordinates"""
    pyautogui.rightClick(x, y)
    return f"Right clicked at {x}, {y}"

def move_to(x: int, y: int):
    """Move mouse to coordinates"""
    pyautogui.moveTo(x, y, duration=0.2)
    return f"Moved mouse to {x}, {y}"

def press_key(key: str):
    """Press a keyboard key"""
    pyautogui.press(key)
    return f"Pressed key: {key}"

def scroll(amount: int):
    """Scroll up or down"""
    pyautogui.scroll(amount)
    return f"Scrolled {amount}"

def type_text(text: str):
    """Type text like a human"""
    pyautogui.write(text, interval=0.05)
    return f"Typed: {text}"

def play_youtube_logic(song_name: str):
    """
    Automated sequence to play a song on YouTube.
    We use keyboard shortcuts for better reliability across resolutions.
    """
    try:
        # Step 1: Open the search results page (most robust start)
        query = song_name.replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={query}"
        
        # We rely on pc_control's open_url to handle browser choice
        from pc_control import open_url
        open_url(url)
        
        # Step 2: Wait for browser and page to load
        time.sleep(4) 
        
        # Step 3: Tab navigation to the first video
        # On most YouTube layouts, 2-3 tabs from search results page gets to the first video
        # But even better: Use 'ENTER' as the first video is often auto-focused
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('enter') # Double tap to be sure
        
        return f"Searching and attempting to play '{song_name}' on YouTube."
    except Exception as e:
        logger.error(f"YouTube automation failed: {e}")
        return f"Failed to automate YouTube: {str(e)}"
