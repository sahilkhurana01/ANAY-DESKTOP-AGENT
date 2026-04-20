"""AI Brain module using Google Gemini API for ANAY."""
import requests
from typing import List, Dict, Optional
import logging
import time
from config import GEMINI_API_KEY, GEMINI_API_URL, GEMINI_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
from memory import ConversationMemory

logger = logging.getLogger(__name__)

# ANAY System Prompt
ANAY_SYSTEM_PROMPT = """You are ANAY, an extremely intelligent and helpful AI assistant. You communicate exclusively in English and are professional and friendly.

CRITICAL RULES:
1. NEVER claim to have done something unless you actually did it
2. NEVER make up file paths - always use real, absolute paths
3. NEVER pretend to execute commands - only acknowledge what was actually executed
4. If you don't know something, admit it honestly
5. WAIT for command execution results before responding

Your capabilities:
- Answer any question accurately and honestly
- Remember conversation context
- Communicate clearly in English only
- Execute REAL system commands (file operations, app launching, screen capture)
- You are smart, helpful, and TRUTHFUL above all

System Control Capabilities:
- Create files: "create file [name] on desktop with [content]"
- Read files: "read file [path]" or "open file [path]"
- Write to files: "write [content] to file [path]"
- Launch apps: "open notepad", "launch vscode", "open chrome"
- Browser: "open youtube.com", "search google for [query]"
- Spotify: "play [song name] on spotify"
- Screen: "what's on my screen?", "take a screenshot"
- Active window: "what window am I in?"

When user gives a command:
1. Extract the command parameters accurately
2. Let the system execute it
3. Respond based on actual execution results
4. NEVER claim success before seeing the result

Always remember: You are ANAY, truthful and capable. Never hallucinate or make up responses."""


class AIBrain:
    """Handles AI interactions using Google Gemini API."""
    
    def __init__(self):
        """Initialize Google Gemini API client."""
        self.api_key = GEMINI_API_KEY
        self.api_url = GEMINI_API_URL
        self.model = GEMINI_MODEL
        logger.info(f"Google Gemini API initialized successfully with model: {self.model}")
    
    def generate_response(
        self,
        user_message: str,
        memory: ConversationMemory,
        language: str = "en"
    ) -> Dict[str, any]:
        """Generate AI response with context awareness."""
        try:
            # Build conversation history
            context = memory.get_context()
            
            # Build contents array for Gemini API
            # v1beta supports systemInstruction
            contents = []
            
            # Add conversation history (last 10 messages)
            for msg in context[-10:]:
                if msg["role"] == "user":
                    contents.append({
                        "role": "user",
                        "parts": [{"text": msg["content"]}]
                    })
                elif msg["role"] == "assistant":
                    contents.append({
                        "role": "model",
                        "parts": [{"text": msg["content"]}]
                    })
            
            contents.append({
                "role": "user",
                "parts": [{"text": user_message}]
            })
            
            # Prepare request payload for Gemini v1beta API with systemInstruction
            payload = {
                "contents": contents,
                "systemInstruction": {
                    "parts": [{"text": ANAY_SYSTEM_PROMPT}]
                },
                "generationConfig": {
                    "temperature": DEFAULT_TEMPERATURE,
                    "maxOutputTokens": DEFAULT_MAX_TOKENS,
                }
            }

            
            # Make API request to Google Gemini with retry logic
            url_with_key = f"{self.api_url}?key={self.api_key}"
            
            max_retries = 3
            base_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        url_with_key,
                        headers={"Content-Type": "application/json"},
                        json=payload,
                        timeout=30
                    )
                    
                    # Check for errors
                    response.raise_for_status()
                    break  # Success, exit retry loop
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:  # Rate limit / quota exceeded
                        if attempt < max_retries - 1:
                            # Exponential backoff
                            delay = base_delay * (2 ** attempt)
                            logger.warning(f"Rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                            continue
                        else:
                            # Max retries reached, handle gracefully
                            logger.error(f"Rate limit exceeded after {max_retries} attempts")
                            raise
                    else:
                        # Other HTTP errors, don't retry
                        raise
            
            response_data = response.json()
            
            # Extract response text from Gemini format
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    ai_response = candidate["content"]["parts"][0]["text"].strip()
                else:
                    ai_response = "Sorry, I didn't receive a valid response from the API."
            else:
                ai_response = "Sorry, I didn't receive a response from the API."
            
            # Check if response contains system command
            command_info = self._extract_command(ai_response, user_message)
            
            return {
                "response": ai_response,
                "command": command_info
            }
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from Gemini API: {e}")
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"Error response: {error_data}")
                except:
                    logger.error(f"Error response text: {e.response.text}")
            
            # Always try to extract commands from user input, even when AI fails
            command_info = self._extract_command("", user_message)
            
            # Provide contextual response based on whether a command was detected
            if command_info:
                command_type = command_info.get("type")
                if command_type == "open_browser":
                    url = command_info.get("url", "")
                    fallback = f"✅ Opening browser: {url}"
                elif command_type == "play_spotify":
                    query = command_info.get("query", "")
                    fallback = f"✅ Opening Spotify{f' - {query}' if query else ''}"
                elif command_type == "launch_app":
                    app_name = command_info.get("name", "")
                    fallback = f"✅ Launching {app_name}"
                elif command_type == "open_file":
                    fallback = "✅ Attempting to open file"
                elif command_type == "open_folder":
                    fallback = "✅ Attempting to open folder"
                else:
                    fallback = "✅ Executing command"
            else:
                fallback = "Sorry, I'm having trouble connecting to the API right now. However, I can still execute system commands for you."
            
            return {
                "response": fallback,
                "command": command_info,
                "error": str(e)
            }
        
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Always try to extract commands from user input, even when AI fails
            command_info = self._extract_command("", user_message)
            
            # Provide contextual response based on whether a command was detected
            if command_info:
                command_type = command_info.get("type")
                if command_type == "open_browser":
                    url = command_info.get("url", "")
                    fallback = f"✅ Opening browser: {url}"
                elif command_type == "play_spotify":
                    query = command_info.get("query", "")
                    fallback = f"✅ Opening Spotify{f' - {query}' if query else ''}"
                elif command_type == "launch_app":
                    app_name = command_info.get("name", "")
                    fallback = f"✅ Launching {app_name}"
                elif command_type == "open_file":
                    fallback = "✅ Attempting to open file"
                elif command_type == "open_folder":
                    fallback = "✅ Attempting to open folder"
                else:
                    fallback = "✅ Executing command"
            else:
                fallback = "Sorry, I'm having trouble responding right now. However, I can still execute system commands for you."

            return {
                "response": fallback,
                "command": command_info,
                "error": str(e)
            }
    
    def _extract_command(self, ai_response: str, user_message: str) -> Optional[Dict[str, any]]:
        """Extract system command from user message or AI response."""
        if not user_message:
            return None
            
        message_lower = user_message.lower().strip()
        response_lower = ai_response.lower() if ai_response else ""
        
        # Fix common typos
        message_lower = message_lower.replace('oprn', 'open')
        message_lower = message_lower.replace('opne', 'open')
        message_lower = message_lower.replace('sptify', 'spotify')
        message_lower = message_lower.replace('whtsapp', 'whatsapp')
        message_lower = message_lower.replace('comapnies', 'companies')
        
        # PRIORITY 1: Application launching (check FIRST before browser)
        # This prevents "open chrome" from opening browser instead of Chrome app
        app_keywords = ['notepad', 'calculator', 'paint', 'vscode', 'chrome', 'brave', 
                       'firefox', 'edge', 'spotify', 'whatsapp', 'telegram', 'discord',
                       'vlc', 'word', 'excel', 'powerpoint']
        
        for app in app_keywords:
            if app in message_lower and ('open' in message_lower or 'launch' in message_lower or 'start' in message_lower):
                # Extract just the app name
                return {"type": "launch_app", "name": app}
        
        # PRIORITY 2: File creation operations
        if any(keyword in message_lower for keyword in ["create file", "make file", "make a"]):
            # Extract file path and content
            import re
            
            # Try to extract filename
            filename_match = re.search(r'(?:file)\s+(?:called|named)?\s*([\w\-\.]+\.\w+)', user_message, re.IGNORECASE)
            if not filename_match:
                # Try simpler pattern
                filename_match = re.search(r'([\w\-]+\.txt|[\w\-]+\.py|[\w\-]+\.json)', user_message, re.IGNORECASE)
            
            if filename_match:
                filename = filename_match.group(1)
                
                # Determine location (desktop, documents, D:, etc.)
                location = "desktop"  # default
                if "d drive" in message_lower or "d:" in message_lower:
                    location = "D:\\\\"
                elif "c drive" in message_lower or "c:" in message_lower:
                    location = "C:\\\\"
                elif "desktop" in message_lower:
                    location = "desktop"
                elif "documents" in message_lower:
                    location = "documents"
                elif "downloads" in message_lower:
                    location = "downloads"
                
                # Extract content if specified
                content = ""
                if "with" in message_lower or "containing" in message_lower or "add" in message_lower:
                    # Try to extract content after "with" or "add"
                    content_match = re.search(r'(?:with|containing|add|and add)\s+(.+?)(?:\s*$)', user_message, re.IGNORECASE)
                    if content_match:
                        content_text = content_match.group(1).strip()
                        # Remove trailing location info
                        content_text = re.sub(r'\s+(?:on|in|to)\s+(?:desktop|d drive|c drive|documents).*$', '', content_text, flags=re.IGNORECASE)
                        content = content_text
                
                # Handle special content requests like "top 10 IT companies"
                if "top 10" in message_lower and ("it comp" in message_lower or "companies" in message_lower):
                    content = """1. Microsoft
2. Apple
3. Amazon
4. Alphabet (Google)
5. Meta Platforms
6. NVIDIA
7. Oracle
8. IBM
9. Salesforce
10. Accenture"""
                
                path = f"{location}/{filename}" if not location.endswith("\\\\") else f"{location}{filename}"
                return {"type": "create_file", "path": path, "content": content}
        
        # PRIORITY 3: File reading operations
        if any(keyword in message_lower for keyword in ["read file", "show file", "file content"]):
            # Extract file path
            parts = user_message.split()
            for i, part in enumerate(parts):
                if part.lower() in ["file"] and i + 1 < len(parts):
                    path = " ".join(parts[i+1:])
                    return {"type": "read_file", "path": path}
        
        # PRIORITY 4: File opening operations
        if any(keyword in message_lower for keyword in ["open file", "file open"]) and "it" not in message_lower:
            # Extract file path
            import re
            # Try to extract path after "open file" or "file"
            path_match = re.search(r'(?:open\\s+file|file)\\s+(.+?)$', user_message, re.IGNORECASE)
            if path_match:
                path = path_match.group(1).strip()
                return {"type": "open_file", "path": path}
        
        # PRIORITY 5: Folder operations
        if any(keyword in message_lower for keyword in ["open folder", "folder open", "folder", "directory"]):
            parts = user_message.split()
            for i, part in enumerate(parts):
                if part.lower() in ["folder", "directory"] and i + 1 < len(parts):
                    path = " ".join(parts[i+1:])
                    return {"type": "open_folder", "path": path}
        
        # PRIORITY 6: Screen capture and analysis operations
        if any(keyword in message_lower for keyword in ["screenshot", "capture screen", "screen capture"]):
            return {"type": "capture_screen", "path": None}
        
        # Screen analysis (what's on my screen, analyze screen, explain screen)
        if any(keyword in message_lower for keyword in ["what's on my screen", "what is on my screen", "analyze screen", "explain screen", "describe screen", "see my screen"]):
            return {"type": "analyze_screen", "path": None}
        
        # PRIORITY 7: Active window detection
        if any(keyword in message_lower for keyword in ["active window", "current window", "what window"]):
            return {"type": "get_active_window"}
        
        # PRIORITY 8: Spotify operations (specific commands)
        if "spotify" in message_lower or ("play" in message_lower and any(word in message_lower for word in ["song", "music", "track", "bars"])):
            # Extract song/query
            import re
            query_match = re.search(r'play\\s+(.+?)(?:\\s+on\\s+spotify|$)', user_message, re.IGNORECASE)
            if query_match:
                query = query_match.group(1).strip()
                # Remove "on spotify" if present
                query = re.sub(r'\\s+on\\s+spotify$', '', query, flags=re.IGNORECASE)
                return {"type": "play_spotify", "query": query}
            else:
                return {"type": "play_spotify", "query": ""}
        
        # PRIORITY 9: System information queries
        if any(keyword in message_lower for keyword in ["system info", "system status", "computer info", "pc info", "system stats"]):
            return {"type": "system_info"}
        
        if any(keyword in message_lower for keyword in ["battery", "battery status", "battery level", "how much battery"]):
            return {"type": "battery_status"}
        
        if any(keyword in message_lower for keyword in ["running processes", "what's running", "active processes", "task manager"]):
            return {"type": "running_processes"}
        
        # PRIORITY 10: Keyboard/Mouse automation
        # Type text
        if any(keyword in message_lower for keyword in ["type ", "write "]):
            import re
            # Extract text to type
            type_match = re.search(r'(?:type|write)\s+(.+?)$', user_message, re.IGNORECASE)
            if type_match:
                text = type_match.group(1).strip()
                return {"type": "type_text", "text": text}
        
        # Press key
        if any(keyword in message_lower for keyword in ["press ", "hit "]):
            import re
            key_match = re.search(r'(?:press|hit)\s+(\w+)', user_message, re.IGNORECASE)
            if key_match:
                key = key_match.group(1).lower()
                return {"type": "press_key", "key": key}
        
        # Hotkey combinations (e.g., "ctrl+c", "alt+tab")
        if "+" in message_lower and any(keyword in message_lower for keyword in ["ctrl", "alt", "shift", "win"]):
            import re
            hotkey_match = re.search(r'((?:ctrl|alt|shift|win)(?:\+\w+)+)', user_message, re.IGNORECASE)
            if hotkey_match:
                keys = hotkey_match.group(1).split('+')
                return {"type": "hotkey", "keys": keys}
        
        # Click mouse
        if "click" in message_lower:
            import re
            # Try to extract coordinates
            coord_match = re.search(r'click\s+(?:at\s+)?\(?([0-9]+)\s*,\s*([0-9]+)\)?', user_message, re.IGNORECASE)
            if coord_match:
                x, y = int(coord_match.group(1)), int(coord_match.group(2))
                return {"type": "click_mouse", "x": x, "y": y, "button": "left", "clicks": 1}
            else:
                # Just click at current position
                return {"type": "click_mouse", "x": None, "y": None, "button": "left", "clicks": 1}
        
        # Scroll
        if "scroll" in message_lower:
            import re
            # Determine direction and amount
            clicks = 3  # default
            direction = "vertical"
            
            if "down" in message_lower:
                clicks = -3
            elif "up" in message_lower:
                clicks = 3
            
            # Try to extract number
            num_match = re.search(r'scroll\s+(?:down|up)?\s*([0-9]+)', user_message, re.IGNORECASE)
            if num_match:
                amount = int(num_match.group(1))
                clicks = -amount if "down" in message_lower else amount
            
            return {"type": "scroll", "clicks": clicks, "direction": direction}
        
        # PRIORITY 10: Browser/URL operations (check LAST to avoid conflicts)
        # Only trigger if it's clearly a URL or website
        if any(keyword in message_lower for keyword in [".com", ".in", ".org", "youtube", "google", "facebook", "twitter", "instagram"]):
            # Handle "open youtube.com" or "search youtube"
            url = user_message.strip()
            
            # Remove common command words
            remove_words = ["open", "browser", "in", "please", "search", "then", "and"]
            for word in remove_words:
                url = url.replace(word, " ").replace(word.capitalize(), " ")
            
            url = " ".join(url.split()).strip()  # Clean up extra spaces
            
            url_lower = url.lower()
            
            # Handle common websites
            if "youtube" in url_lower:
                url = "https://www.youtube.com"
            elif "google" in url_lower:
                url = "https://www.google.com"
            elif "facebook" in url_lower:
                url = "https://www.facebook.com"
            elif "twitter" in url_lower or "x.com" in url_lower:
                url = "https://www.x.com"
            elif "instagram" in url_lower:
                url = "https://www.instagram.com"
            elif "github" in url_lower:
                url = "https://www.github.com"
            elif not url.startswith(("http://", "https://")):
                # If it looks like a domain, add https://
                if "." in url and not url.startswith("/"):
                    url = "https://" + url
                else:
                    return None  # Not a valid URL
            
            return {"type": "open_browser", "url": url}
        
        return None


# Global AI brain instance
ai_brain = AIBrain()
