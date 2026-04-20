"""Cross-platform system control module for ANAY."""
import os
import platform
import subprocess
import shlex
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging
import base64
from io import BytesIO
import requests

logger = logging.getLogger(__name__)


class SystemController:
    """Handles system-level operations across platforms."""
    
    def __init__(self):
        self.platform = platform.system()
        self.allowed_extensions = [
            '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3', '.wav', '.avi',
            '.zip', '.rar', '.7z', '.py', '.js', '.html', '.css', '.json', '.xml'
        ]
        
        # Get user profile directory
        if self.platform == "Windows":
            self.user_profile = os.environ.get('USERPROFILE', '')
            self.desktop = os.path.join(self.user_profile, 'Desktop')
            self.documents = os.path.join(self.user_profile, 'Documents')
            self.downloads = os.path.join(self.user_profile, 'Downloads')
        else:
            self.user_profile = os.path.expanduser('~')
            self.desktop = os.path.join(self.user_profile, 'Desktop')
            self.documents = os.path.join(self.user_profile, 'Documents')
            self.downloads = os.path.join(self.user_profile, 'Downloads')
        
        # Common application paths (Windows)
        self.app_paths = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'vscode': [
                os.path.join(self.user_profile, r'AppData\Local\Programs\Microsoft VS Code\Code.exe'),
                r'C:\Program Files\Microsoft VS Code\Code.exe',
                r'C:\Program Files (x86)\Microsoft VS Code\Code.exe'
            ],
            'chrome': [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                os.path.join(self.user_profile, r'AppData\Local\Google\Chrome\Application\chrome.exe')
            ],
            'brave': [
                r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
                r'C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe',
                os.path.join(self.user_profile, r'AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe')
            ],
            'firefox': [
                r'C:\Program Files\Mozilla Firefox\firefox.exe',
                r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
            ],
            'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            'spotify': os.path.join(self.user_profile, r'AppData\Roaming\Spotify\Spotify.exe'),
            'whatsapp': 'shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App',
            'telegram': os.path.join(self.user_profile, r'AppData\Roaming\Telegram Desktop\Telegram.exe'),
            'discord': os.path.join(self.user_profile, r'AppData\Local\Discord\Update.exe'),
            'vlc': r'C:\Program Files\VideoLAN\VLC\vlc.exe',
            'word': r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE',
            'excel': r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE',
            'powerpoint': r'C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE',
        }
    
    def _resolve_path(self, path: str) -> str:
        """Resolve path shortcuts like 'desktop', 'documents', etc."""
        path_lower = path.lower().strip()
        
        # Handle special folder names
        if path_lower == 'desktop' or path_lower.startswith('desktop\\') or path_lower.startswith('desktop/'):
            return path.replace('desktop', self.desktop, 1).replace('Desktop', self.desktop, 1)
        elif path_lower == 'documents' or path_lower.startswith('documents\\') or path_lower.startswith('documents/'):
            return path.replace('documents', self.documents, 1).replace('Documents', self.documents, 1)
        elif path_lower == 'downloads' or path_lower.startswith('downloads\\') or path_lower.startswith('downloads/'):
            return path.replace('downloads', self.downloads, 1).replace('Downloads', self.downloads, 1)
        
        # Expand user home directory
        path = os.path.expanduser(path)
        
        return path
    
    def _validate_path(self, path: str, must_exist: bool = True) -> Tuple[bool, Optional[str]]:
        """Validate file/folder path for security."""
        try:
            # Resolve path to prevent directory traversal
            resolved = Path(self._resolve_path(path)).resolve()
            
            # Check if path exists (if required)
            if must_exist and not resolved.exists():
                return False, f"Path does not exist: {path}"
            
            # Check path length
            if len(str(resolved)) > 500:
                return False, "Path too long"
            
            return True, None
        except Exception as e:
            return False, f"Invalid path: {str(e)}"
    
    # ==================== FILE OPERATIONS ====================
    
    def create_file(self, file_path: str, content: str = "") -> Dict[str, any]:
        """Create a new file with optional content."""
        try:
            # Resolve path
            resolved_path = self._resolve_path(file_path)
            path = Path(resolved_path).resolve()
            
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"Created file: {path.name}",
                "path": str(path)
            }
        except Exception as e:
            logger.error(f"Error creating file: {e}")
            return {"success": False, "error": str(e)}
    
    def read_file(self, file_path: str) -> Dict[str, any]:
        """Read contents of a file."""
        is_valid, error = self._validate_path(file_path, must_exist=True)
        if not is_valid:
            return {"success": False, "error": error}
        
        try:
            resolved_path = self._resolve_path(file_path)
            path = Path(resolved_path).resolve()
            
            if not path.is_file():
                return {"success": False, "error": "Path is not a file"}
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "message": f"Read file: {path.name}",
                "content": content,
                "path": str(path)
            }
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return {"success": False, "error": str(e)}
    
    def write_file(self, file_path: str, content: str, append: bool = False) -> Dict[str, any]:
        """Write or append content to a file."""
        try:
            resolved_path = self._resolve_path(file_path)
            path = Path(resolved_path).resolve()
            
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(path, mode, encoding='utf-8') as f:
                f.write(content)
            
            action = "Appended to" if append else "Wrote to"
            return {
                "success": True,
                "message": f"{action} file: {path.name}",
                "path": str(path)
            }
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            return {"success": False, "error": str(e)}
    
    def open_file(self, file_path: str) -> Dict[str, any]:
        """Open a file with the default application."""
        is_valid, error = self._validate_path(file_path)
        if not is_valid:
            return {"success": False, "error": error}
        
        try:
            resolved_path = self._resolve_path(file_path)
            path = Path(resolved_path).resolve()
            
            if self.platform == "Windows":
                os.startfile(str(path))
            elif self.platform == "Darwin":  # macOS
                subprocess.run(["open", str(path)], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", str(path)], check=True)
            
            return {"success": True, "message": f"Opened file: {path.name}"}
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return {"success": False, "error": str(e)}
    
    def open_folder(self, folder_path: str) -> Dict[str, any]:
        """Open a folder in the file explorer."""
        is_valid, error = self._validate_path(folder_path)
        if not is_valid:
            return {"success": False, "error": error}
        
        try:
            resolved_path = self._resolve_path(folder_path)
            path = Path(resolved_path).resolve()
            
            if not path.is_dir():
                return {"success": False, "error": "Path is not a directory"}
            
            if self.platform == "Windows":
                os.startfile(str(path))
            elif self.platform == "Darwin":  # macOS
                subprocess.run(["open", str(path)], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", str(path)], check=True)
            
            return {"success": True, "message": f"Opened folder: {path.name}"}
        except Exception as e:
            logger.error(f"Error opening folder: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== SCREEN CAPTURE ====================
    
    def capture_screenshot(self, save_path: Optional[str] = None) -> Dict[str, any]:
        """Capture a screenshot of the current screen."""
        try:
            import pyautogui
            from PIL import Image
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Save if path provided
            if save_path:
                resolved_path = self._resolve_path(save_path)
                path = Path(resolved_path).resolve()
                path.parent.mkdir(parents=True, exist_ok=True)
                screenshot.save(str(path))
                
                return {
                    "success": True,
                    "message": "Screenshot captured and saved",
                    "path": str(path),
                    "image": screenshot
                }
            else:
                # Return image as base64
                buffered = BytesIO()
                screenshot.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                return {
                    "success": True,
                    "message": "Screenshot captured",
                    "image_base64": img_str,
                    "image": screenshot
                }
        except ImportError:
            return {
                "success": False,
                "error": "Screenshot libraries not installed. Run: pip install pillow pyautogui"
            }
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return {"success": False, "error": str(e)}
    
    def get_active_window(self) -> Dict[str, any]:
        """Get information about the currently active window."""
        try:
            if self.platform == "Windows":
                import pygetwindow as gw
                active = gw.getActiveWindow()
                if active:
                    return {
                        "success": True,
                        "title": active.title,
                        "position": {"x": active.left, "y": active.top},
                        "size": {"width": active.width, "height": active.height}
                    }
                else:
                    return {"success": False, "error": "No active window found"}
            else:
                return {"success": False, "error": "Active window detection only supported on Windows"}
        except ImportError:
            return {
                "success": False,
                "error": "Window detection library not installed. Run: pip install pygetwindow"
            }
        except Exception as e:
            logger.error(f"Error getting active window: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_screen(self, screenshot_path: Optional[str] = None) -> Dict[str, any]:
        """Analyze screen using Gemini Vision API."""
        try:
            # Capture screenshot if not provided
            if screenshot_path:
                from PIL import Image
                screenshot = Image.open(screenshot_path)
            else:
                screenshot_result = self.capture_screenshot()
                if not screenshot_result.get("success"):
                    return screenshot_result
                screenshot = screenshot_result["image"]
            
            # Convert image to base64
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Get Gemini API key from environment
            from config import GEMINI_API_KEY, GEMINI_API_URL
            
            # Prepare vision API request
            # Use Gemini Vision model
            vision_url = GEMINI_API_URL.replace("gemini-1.5-flash", "gemini-1.5-flash")
            url_with_key = f"{vision_url}?key={GEMINI_API_KEY}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Analyze this screenshot and describe what you see. Include: 1) What application/window is open, 2) What the user is working on, 3) Any important details or context."},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": img_base64
                            }
                        }
                    ]
                }]
            }
            
            response = requests.post(
                url_with_key,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            # Extract analysis from response
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    analysis = candidate["content"]["parts"][0]["text"].strip()
                    return {
                        "success": True,
                        "analysis": analysis,
                        "message": "Screen analyzed successfully"
                    }
            
            return {"success": False, "error": "Could not analyze screenshot"}
            
        except ImportError:
            return {
                "success": False,
                "error": "Required libraries not installed. Run: pip install pillow requests"
            }
        except Exception as e:
            logger.error(f"Error analyzing screen: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== APPLICATION LAUNCHER ====================
    
    def launch_application(self, app_name: str, app_path: Optional[str] = None) -> Dict[str, any]:
        """Launch an application by name or path."""
        try:
            if app_path:
                # Launch by path
                is_valid, error = self._validate_path(app_path)
                if not is_valid:
                    return {"success": False, "error": error}
                
                path = Path(app_path).resolve()
                
                if self.platform == "Windows":
                    subprocess.Popen([str(path)], shell=True)
                else:
                    subprocess.Popen([str(path)])
                
                return {"success": True, "message": f"Launched application: {path.name}"}
            else:
                # Launch by name
                app_name_lower = app_name.lower().strip()
                
                # Check if app is in predefined paths
                if app_name_lower in self.app_paths:
                    app_info = self.app_paths[app_name_lower]
                    
                    # Handle list of possible paths
                    if isinstance(app_info, list):
                        for path in app_info:
                            if os.path.exists(path):
                                if self.platform == "Windows":
                                    subprocess.Popen([path], shell=True)
                                else:
                                    subprocess.Popen([path])
                                return {"success": True, "message": f"Launched {app_name}"}
                        return {"success": False, "error": f"{app_name} not found. Please install it."}
                    else:
                        # Single path
                        if app_info.startswith('shell:'):
                            # Windows Store app
                            subprocess.Popen(['explorer.exe', app_info], shell=True)
                            return {"success": True, "message": f"Launched {app_name}"}
                        elif os.path.exists(app_info):
                            if self.platform == "Windows":
                                subprocess.Popen([app_info], shell=True)
                            else:
                                subprocess.Popen([app_info])
                            return {"success": True, "message": f"Launched {app_name}"}
                        else:
                            # Try to launch directly (for system apps like notepad)
                            if self.platform == "Windows":
                                subprocess.Popen([app_info], shell=True)
                            else:
                                subprocess.Popen([app_info])
                            return {"success": True, "message": f"Launched {app_name}"}
                else:
                    # Try to launch directly
                    if self.platform == "Windows":
                        subprocess.Popen([app_name], shell=True)
                    elif self.platform == "Darwin":
                        subprocess.Popen(["open", "-a", app_name])
                    else:
                        subprocess.Popen([app_name])
                    
                    return {"success": True, "message": f"Launched application: {app_name}"}
        except Exception as e:
            logger.error(f"Error launching application: {e}")
            return {"success": False, "error": f"Could not launch {app_name}: {str(e)}"}
    
    def open_browser(self, url: str = "") -> Dict[str, any]:
        """Open a URL in the default browser."""
        try:
            if not url:
                url = "https://www.google.com"
            
            # Validate URL format
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            
            if self.platform == "Windows":
                import webbrowser
                webbrowser.open(url)
            elif self.platform == "Darwin":  # macOS
                subprocess.run(["open", url], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", url], check=True)
            
            return {"success": True, "message": f"Opened browser: {url}"}
        except Exception as e:
            logger.error(f"Error opening browser: {e}")
            return {"success": False, "error": str(e)}
    
    def play_spotify(self, query: str = "") -> Dict[str, any]:
        """Control Spotify playback."""
        try:
            if self.platform == "Windows":
                # Windows - try Spotify URI or Web API
                # For now, we'll try to open Spotify app
                try:
                    spotify_path = self.app_paths.get('spotify', 'spotify')
                    if os.path.exists(spotify_path):
                        subprocess.Popen([spotify_path], shell=True)
                    else:
                        subprocess.Popen(["spotify"], shell=True)
                    
                    if query:
                        # Note: Full Spotify control requires Spotify Web API or COM automation
                        return {
                            "success": True,
                            "message": f"Opened Spotify. Search for: {query}",
                            "note": "Full control requires Spotify Web API integration"
                        }
                    return {"success": True, "message": "Opened Spotify"}
                except:
                    return {"success": False, "error": "Spotify not found. Please install Spotify."}
            
            elif self.platform == "Darwin":
                # macOS - use AppleScript
                if query:
                    script = f'tell application "Spotify" to play track "{query}"'
                else:
                    script = 'tell application "Spotify" to play'
                
                subprocess.run(["osascript", "-e", script], check=True)
                return {"success": True, "message": f"Playing on Spotify: {query or 'current track'}"}
            
            else:
                # Linux - try dbus or spotify CLI
                try:
                    if query:
                        subprocess.run(["dbus-send", "--print-reply", "--dest=org.mpris.MediaPlayer2.spotify",
                                       "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player.OpenUri",
                                       f"string:spotify:search:{query}"], check=True)
                    else:
                        subprocess.run(["dbus-send", "--print-reply", "--dest=org.mpris.MediaPlayer2.spotify",
                                       "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player.Play"],
                                      check=True)
                    return {"success": True, "message": f"Playing on Spotify: {query or 'current track'}"}
                except:
                    return {"success": False, "error": "Spotify control not available on Linux. Install Spotify and ensure DBus is configured."}
        
        except Exception as e:
            logger.error(f"Error controlling Spotify: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== SYSTEM INFORMATION ====================
    
    def get_system_info(self) -> Dict[str, any]:
        """Get comprehensive system information."""
        try:
            import psutil
            
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory info
            memory = psutil.virtual_memory()
            memory_total_gb = memory.total / (1024 ** 3)
            memory_used_gb = memory.used / (1024 ** 3)
            memory_percent = memory.percent
            
            # Disk info
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024 ** 3)
            disk_used_gb = disk.used / (1024 ** 3)
            disk_percent = disk.percent
            
            # Battery info (if available)
            battery_info = {}
            try:
                battery = psutil.sensors_battery()
                if battery:
                    battery_info = {
                        "percent": battery.percent,
                        "plugged_in": battery.power_plugged,
                        "time_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Unlimited"
                    }
            except:
                battery_info = {"available": False}
            
            return {
                "success": True,
                "cpu": {
                    "usage_percent": cpu_percent,
                    "cores": cpu_count
                },
                "memory": {
                    "total_gb": round(memory_total_gb, 2),
                    "used_gb": round(memory_used_gb, 2),
                    "percent": memory_percent
                },
                "disk": {
                    "total_gb": round(disk_total_gb, 2),
                    "used_gb": round(disk_used_gb, 2),
                    "percent": disk_percent
                },
                "battery": battery_info,
                "platform": self.platform
            }
        except ImportError:
            return {"success": False, "error": "psutil not installed. Run: pip install psutil"}
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"success": False, "error": str(e)}
    
    def get_battery_status(self) -> Dict[str, any]:
        """Get battery status."""
        try:
            import psutil
            battery = psutil.sensors_battery()
            
            if battery is None:
                return {"success": False, "error": "No battery detected (desktop computer?)"}
            
            return {
                "success": True,
                "percent": battery.percent,
                "plugged_in": battery.power_plugged,
                "time_left_seconds": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
                "message": f"Battery at {battery.percent}% ({'Charging' if battery.power_plugged else 'Discharging'})"
            }
        except ImportError:
            return {"success": False, "error": "psutil not installed"}
        except Exception as e:
            logger.error(f"Error getting battery status: {e}")
            return {"success": False, "error": str(e)}
    
    def get_running_processes(self, limit: int = 10) -> Dict[str, any]:
        """Get list of running processes."""
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            return {
                "success": True,
                "processes": processes[:limit],
                "total_count": len(processes)
            }
        except ImportError:
            return {"success": False, "error": "psutil not installed"}
        except Exception as e:
            logger.error(f"Error getting processes: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== KEYBOARD & MOUSE AUTOMATION ====================
    
    def type_text(self, text: str, interval: float = 0.0) -> Dict[str, any]:
        """Type text using keyboard automation."""
        try:
            import pyautogui
            pyautogui.write(text, interval=interval)
            return {
                "success": True,
                "message": f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}"
            }
        except ImportError:
            return {"success": False, "error": "pyautogui not installed"}
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return {"success": False, "error": str(e)}
    
    def press_key(self, key: str, presses: int = 1) -> Dict[str, any]:
        """Press a keyboard key."""
        try:
            import pyautogui
            pyautogui.press(key, presses=presses)
            return {
                "success": True,
                "message": f"Pressed key: {key} ({presses} time(s))"
            }
        except ImportError:
            return {"success": False, "error": "pyautogui not installed"}
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            return {"success": False, "error": str(e)}
    
    def hotkey(self, *keys) -> Dict[str, any]:
        """Press a keyboard hotkey combination."""
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
            return {
                "success": True,
                "message": f"Pressed hotkey: {'+'.join(keys)}"
            }
        except ImportError:
            return {"success": False, "error": "pyautogui not installed"}
        except Exception as e:
            logger.error(f"Error pressing hotkey: {e}")
            return {"success": False, "error": str(e)}
    
    def click_mouse(self, x: Optional[int] = None, y: Optional[int] = None, 
                    button: str = 'left', clicks: int = 1) -> Dict[str, any]:
        """Click mouse at specified position or current position."""
        try:
            import pyautogui
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks, button=button)
                return {
                    "success": True,
                    "message": f"Clicked {button} button at ({x}, {y}) {clicks} time(s)"
                }
            else:
                pyautogui.click(clicks=clicks, button=button)
                return {
                    "success": True,
                    "message": f"Clicked {button} button {clicks} time(s)"
                }
        except ImportError:
            return {"success": False, "error": "pyautogui not installed"}
        except Exception as e:
            logger.error(f"Error clicking mouse: {e}")
            return {"success": False, "error": str(e)}
    
    def move_mouse(self, x: int, y: int, duration: float = 0.0) -> Dict[str, any]:
        """Move mouse to specified position."""
        try:
            import pyautogui
            pyautogui.moveTo(x, y, duration=duration)
            return {
                "success": True,
                "message": f"Moved mouse to ({x}, {y})"
            }
        except ImportError:
            return {"success": False, "error": "pyautogui not installed"}
        except Exception as e:
            logger.error(f"Error moving mouse: {e}")
            return {"success": False, "error": str(e)}
    
    def scroll(self, clicks: int, direction: str = 'vertical') -> Dict[str, any]:
        """Scroll mouse wheel."""
        try:
            import pyautogui
            if direction == 'vertical':
                pyautogui.scroll(clicks)
            else:
                pyautogui.hscroll(clicks)
            return {
                "success": True,
                "message": f"Scrolled {direction}ly {abs(clicks)} clicks {'down' if clicks < 0 else 'up'}"
            }
        except ImportError:
            return {"success": False, "error": "pyautogui not installed"}
        except Exception as e:
            logger.error(f"Error scrolling: {e}")
            return {"success": False, "error": str(e)}
    
    def get_mouse_position(self) -> Dict[str, any]:
        """Get current mouse position."""
        try:
            import pyautogui
            x, y = pyautogui.position()
            return {
                "success": True,
                "x": x,
                "y": y,
                "message": f"Mouse position: ({x}, {y})"
            }
        except ImportError:
            return {"success": False, "error": "pyautogui not installed"}
        except Exception as e:
            logger.error(f"Error getting mouse position: {e}")
            return {"success": False, "error": str(e)}


# Global system controller instance
system_controller = SystemController()
