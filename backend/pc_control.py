"""
Local desktop control tools for ANAY Desktop.
ACTUALLY runs things on the PC using standard Windows commands.
"""
import subprocess
import os
import sys
import time
import shutil
import socket
from typing import Any, Dict, List, Optional
import logging
import inspect
import platform
import webbrowser
import psutil
import pyperclip
import pyautogui
import ctypes
import urllib.parse
from pathlib import Path

logger = logging.getLogger(__name__)

# Disable failsafe to prevent accidental triggers from stopping the whole AI
pyautogui.FAILSAFE = False

def save_contact(name: str, phone: str, **kwargs) -> str:
    from memory import save_contact as db_save
    db_save(name, phone)
    return f"Saved {name}'s number: {phone}"

def open_app(name: str) -> str:
    """Open any application by name"""
    name_lower = name.lower().strip()
    
    # App name → actual executable mapping (Windows)
    WIN_APPS = {
        "chrome": "start chrome",
        "brave": "start brave",
        "spotify": "start spotify",
        "notepad": "start notepad",
        "vscode": "start code",
        "terminal": "start cmd",
        "whatsapp": "start whatsapp",
        "calculator": "start calc",
        "edge": "start msedge",
    }
    
    cmd = WIN_APPS.get(name_lower)
    if cmd:
        try:
            subprocess.Popen(cmd, shell=True)
            return f"Opened {name}"
        except: pass
    
    # Try system search
    try:
        where_res = subprocess.run(["where", name_lower + ".exe"], capture_output=True, text=True, timeout=2)
        if where_res.returncode == 0:
            path = where_res.stdout.splitlines()[0]
            subprocess.Popen([path])
            return f"Opened {name} via PATH"
    except: pass

    # Sahil specific paths
    user = "Sahil khurana"
    fallbacks = {
        "spotify": [rf"C:\Users\{user}\AppData\Roaming\Spotify\Spotify.exe"],
        "whatsapp": [
            rf"C:\Users\{user}\AppData\Local\WhatsApp\WhatsApp.exe",
            rf"C:\Users\{user}\AppData\Local\WhatsApp\app.exe",
            r"shell:AppsFolder\WhatsApp.WhatsApp_8wekyb3d8bbwe!App"
        ]
    }
    
    if name_lower in fallbacks:
        for p in fallbacks[name_lower]:
            if p.startswith("shell:"):
                try:
                    subprocess.Popen(f"start {p}", shell=True)
                    return f"Opened {name} via Store"
                except: continue
            if os.path.exists(p):
                subprocess.Popen([p])
                return f"Opened {name} via Path"

    # Last resort
    subprocess.Popen(f"start {name_lower}", shell=True)
    return f"Tried to open {name}"

def close_app(name: str) -> str:
    killed = []
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if name.lower() in (proc.info.get('name') or "").lower():
                proc.kill()
                killed.append(proc.info.get('name') or str(proc.pid))
        except:
            pass
    return f"Closed: {killed}" if killed else f"Not found: {name}"

def open_url(url: str) -> str:
    """Open URL — tries Brave first, then default browser"""
    brave_paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    for path in brave_paths:
        if os.path.exists(path):
            subprocess.Popen([path, url])
            return f"Opened in Brave: {url}"
    # fallback to default browser
    webbrowser.open(url)
    return f"Opened: {url}"

def play_media(name: str) -> str:
    """Play media — opens Spotify or YouTube search"""
    name_lower = name.lower()
    if "spotify" in name_lower:
        subprocess.Popen("start spotify", shell=True)
        return f"Opened Spotify"
    else:
        query = name_lower.replace("spotify", "").replace("youtube", "").strip()
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        return open_url(url)

def type_text(text: str) -> str:
    pyautogui.write(text, interval=0.05)
    return f"Typed: {text}"

def run_terminal_command(cmd: str) -> str:
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        return (result.stdout + result.stderr).strip() or "Command ran (no output)"
    except Exception as e:
        return f"Error: {e}"

def get_system_stats() -> dict:
    battery = psutil.sensors_battery()
    disk_path = "C:\\" if sys.platform == "win32" else "/"
    try:
        disk_pct = psutil.disk_usage(disk_path).percent
    except Exception:
        disk_pct = 0.0
    try:
        uptime_seconds = max(0, int(time.time() - psutil.boot_time()))
    except Exception:
        uptime_seconds = 0
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "Unknown"
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_used_gb": round(psutil.virtual_memory().used / 1e9, 1),
        "disk_percent": disk_pct,
        "battery": battery.percent if battery else "N/A",
        "charging": battery.power_plugged if battery else "N/A",
        "battery_percent": battery.percent if battery else None,
        "battery_plugged": battery.power_plugged if battery else None,
        "hostname": hostname,
        "platform": platform.system(),
        "uptime_seconds": uptime_seconds,
    }

def take_screenshot() -> str:
    try:
        import mss, base64
        from PIL import Image
        from io import BytesIO
        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[0])
            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
            img = img.resize((1280, 720))
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=60)
            return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return f"Screenshot failed: {e}"

def read_clipboard() -> str:
    return pyperclip.paste()

def write_clipboard(text: str) -> str:
    pyperclip.copy(text)
    return "Copied to clipboard"

def list_running_apps() -> list:
    apps = set()
    for proc in psutil.process_iter(['name']):
        try: apps.add(proc.info['name'])
        except: pass
    return sorted(list(apps))[:30]

def set_volume(level: int) -> str:
    """Set volume 0-100 using Windows Core Audio API"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        # Convert 0-100 to 0.0-1.0
        scalar = max(0.0, min(1.0, level / 100.0))
        volume.SetMasterVolumeLevelScalar(scalar, None)
        return f"Volume set to {level}%"
    except ImportError:
        # Fallback: PowerShell method
        subprocess.run(
            ["powershell", "-Command",
             f"$obj = New-Object -ComObject WScript.Shell; "
             f"$obj.SendKeys([char]174*50); "  # mute first
             f"Add-Type -TypeDefinition 'using System.Runtime.InteropServices; "
             f"public class Audio {{ [DllImport(\"winmm.dll\")] public static extern int waveOutSetVolume(IntPtr h, uint v); }}';"
             f"[Audio]::waveOutSetVolume([IntPtr]::Zero, {int(level/100 * 0xFFFF) + int(level/100 * 0xFFFF) * 0x10000})"],
            capture_output=True
        )
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Volume error: {e}"

def volume_up(amount: int = 10) -> str:
    """Increase volume by amount"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = min(1.0, current + amount/100.0)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        return f"Volume increased to {int(new_vol*100)}%"
    except Exception as e:
        return f"Error: {e}"

def volume_down(amount: int = 10) -> str:
    """Decrease volume by amount"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = max(0.0, current - amount/100.0)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        return f"Volume decreased to {int(new_vol*100)}%"
    except Exception as e:
        return f"Error: {e}"

def mute_volume() -> str:
    import pyautogui
    pyautogui.press('volumemute')
    return "Muted/Unmuted volume"

def get_volume() -> str:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        return f"Current volume: {int(current*100)}%"
    except Exception as e:
        return f"Error: {e}"

def lock_screen() -> str:
    subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
    return "Screen locked"

def shutdown_pc() -> str:
    subprocess.run("shutdown /s /t 10", shell=True)
    return "Shutting down in 10 seconds"

def open_youtube() -> str:
    return open_url("https://www.youtube.com")

def focus_window(title: str) -> str:
    """Focus a window by its title"""
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title)
        if windows:
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            return f"Focused window: {win.title}"
        return f"No window found with title: {title}"
    except Exception as e:
        return f"Focus failed: {e}"

def list_apps() -> List[str]:
    """List common running application names"""
    apps = set()
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info.get('name')
            if name: apps.add(name.split('.')[0])
        except: pass
    return sorted(list(apps))[:40]

def click_mouse(x: int, y: int, clicks: int = 1) -> str:
    """Click mouse at coordinates"""
    pyautogui.click(x, y, clicks=clicks)
    return f"Clicked at {x}, {y} ({clicks} times)"

def move_mouse(x: int, y: int) -> str:
    """Move mouse to coordinates"""
    pyautogui.moveTo(x, y, duration=0.2)
    return f"Moved mouse to {x}, {y}"

def scroll_mouse(amount: int) -> str:
    """Scroll mouse (positive for up, negative for down)"""
    pyautogui.scroll(amount)
    return f"Scrolled {amount}"

def search_web(query: str) -> str:
    q = urllib.parse.quote_plus(query.strip())
    return open_url(f"https://www.google.com/search?q={q}")


def scroll(direction: str, amount: Optional[int] = None) -> str:
    n = 3 if amount is None else max(1, int(amount))
    delta = n if direction.lower() == "up" else -n
    return scroll_mouse(delta)


def click_at(x: int, y: int) -> str:
    return click_mouse(int(x), int(y), 1)


def move_file(src: str, dest: str) -> str:
    shutil.move(src, dest)
    return f"Moved to {dest}"


def delete_local_file(path: str) -> str:
    p = Path(path)
    if p.is_dir():
        shutil.rmtree(p)
        return f"Removed folder: {path}"
    p.unlink(missing_ok=True)
    return f"Removed file: {path}"


def read_text_file(path: str) -> str:
    data = Path(path).read_text(encoding="utf-8", errors="replace")
    if len(data) > 120_000:
        return data[:120_000] + "\n…(truncated)"
    return data


def write_text_file(path: str, content: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} bytes to {path}"


def send_email(to: str, subject: str, body: str) -> str:
    host = os.getenv("ANAY_SMTP_HOST")
    user = os.getenv("ANAY_SMTP_USER")
    password = os.getenv("ANAY_SMTP_PASS")
    port = int(os.getenv("ANAY_SMTP_PORT", "587"))
    if not host or not user or password is None:
        return "Email not configured. Set ANAY_SMTP_HOST, ANAY_SMTP_USER, ANAY_SMTP_PASS (and optionally ANAY_SMTP_PORT)."
    try:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = user
        msg["To"] = to
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.sendmail(user, [to], msg.as_string())
        return f"Email sent to {to}"
    except Exception as e:
        return f"Email failed: {e}"


def set_reminder(task: str, time: str) -> str:
    from memory import memory_store

    memory_store.save_reminder(task, time)
    return f"Reminder set: {task} @ {time}"


def restart_pc() -> str:
    if sys.platform == "win32":
        subprocess.run("shutdown /r /t 15", shell=True)
        return "Restart scheduled in 15 seconds."
    if sys.platform == "darwin":
        subprocess.Popen(
            ["osascript", "-e", 'tell application "System Events" to restart'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return "Restart initiated."
    return "Restart must be triggered manually on this OS."


def save_user_fact(key: str, value: str) -> str:
    from memory import save_fact
    save_fact(key, value)
    return f"Saved fact: {key} = {value}"


def save_important_memory(memory: str) -> str:
    from memory import save_memory
    save_memory(memory)
    return f"Saved important memory: {memory}"


def _youtube_watch_url_ytdlp(query: str) -> Optional[str]:
    """Resolve the top YouTube search hit to a watch URL (no browser UI guessing)."""
    try:
        import yt_dlp
    except ImportError:
        return None
    q = query.strip()
    if not q:
        return None
    try:
        opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{q}", download=False)
    except Exception as exc:
        print(f"[ANAY] yt-dlp search failed: {exc}")
        return None
    if not info:
        return None
    entries = info.get("entries") or []
    if entries:
        first = entries[0]
        vid = first.get("id")
        if isinstance(vid, str) and len(vid) == 11:
            return f"https://www.youtube.com/watch?v={vid}"
        url = first.get("url") or ""
        if "watch?v=" in url:
            return url.split("&")[0]
        return None
    vid = info.get("id")
    if isinstance(vid, str) and len(vid) == 11:
        return f"https://www.youtube.com/watch?v={vid}"
    return None


def _youtube_dismiss_cookie_banner(page) -> None:
    """Best-effort consent / cookie banners on youtube.com."""
    selectors = [
        'button:has-text("Accept all")',
        'button:has-text("Reject all")',
        'tp-yt-paper-button:has-text("Accept all")',
        '[aria-label="Accept the use of cookies and other data for the purposes described"]',
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1200):
                loc.click(timeout=4000)
                page.wait_for_timeout(600)
                break
        except Exception:
            continue


def _youtube_watch_url_playwright(query: str) -> Optional[str]:
    """Load results in headless Chromium and read the first /watch?v= link from the DOM."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    q = urllib.parse.quote_plus(query.strip())
    search_url = f"https://www.youtube.com/results?search_query={q}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
            try:
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1366, "height": 900},
                    locale="en-US",
                )
                page = context.new_page()
                page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(2200)
                _youtube_dismiss_cookie_banner(page)
                page.wait_for_timeout(400)
                # First few organic results (skip non-watch links)
                loc = page.locator('ytd-video-renderer a[href*="/watch?v="]').first
                loc.wait_for(state="visible", timeout=25000)
                href = loc.get_attribute("href")
                if not href:
                    return None
                if href.startswith("/"):
                    href = "https://www.youtube.com" + href
                if "watch?v=" not in href:
                    return None
                base = href.split("&")[0]
                return base
            finally:
                browser.close()
    except Exception as exc:
        print(f"[ANAY] Playwright YouTube extract failed: {exc}")
        return None


def play_youtube_automated(song_name: str) -> str:
    """
    Open the top YouTube search result as a direct watch URL in the user's browser.

    Uses yt-dlp (ytsearch1) first, then Playwright DOM extraction — avoids Tab/Enter
    which often hits the logo or chrome instead of the first video.
    """
    query = song_name.strip()
    if not query:
        return "No song or search text given."

    print(f"[ANAY] Resolving YouTube top result for: {query!r}")

    watch = _youtube_watch_url_ytdlp(query)
    method = "yt-dlp"
    if not watch:
        watch = _youtube_watch_url_playwright(query)
        method = "playwright"

    if watch:
        open_url(watch)
        return f"Opened top video ({method}) for {query!r}: {watch}"

    # Last resort: results page only (no fake Tab/Enter on wrong control)
    q_enc = urllib.parse.quote_plus(query)
    open_url(f"https://www.youtube.com/results?search_query={q_enc}")
    return (
        f"Could not resolve the first video automatically for {query!r}. "
        "Opened search results — install/update dependencies: pip install yt-dlp playwright && playwright install chromium."
    )

import threading

def send_whatsapp(recipient: str, message: str, **kwargs) -> str:
    """Send a WhatsApp message via WhatsApp Web (by number or name search)"""
    import time
    import pyautogui
    
    # Remove non-digits to check if it's a phone number
    clean_number = "".join(filter(str.isdigit, recipient))
    
    # Check memory for contact number first
    if not clean_number.isdigit() or len(clean_number) < 10:
        from memory import get_contact_number
        db_number = get_contact_number(recipient)
        if db_number:
            print(f"[ANAY] Found number for {recipient} in brain: {db_number}")
            recipient = db_number
            clean_number = "".join(filter(str.isdigit, recipient))

    def _send_logic():
        try:
            # CASE 1: Recipient is likely a phone number
            if len(clean_number) >= 10 and clean_number.isdigit():
                num_to_use = clean_number
                if len(num_to_use) == 10:
                    num_to_use = "91" + num_to_use
                
                encoded_msg = urllib.parse.quote(message)
                url = f"https://web.whatsapp.com/send?phone={num_to_use}&text={encoded_msg}"
                print(f"[ANAY] Opening WhatsApp URL for number: {num_to_use}")
                open_url(url)
                
                # Wait for WhatsApp Web to load and populate the message box
                time.sleep(20) 
                
                # Triple tap Enter to send (one to focus, one to send, one for luck)
                print(f"[ANAY] Hitting Enter to send message to {num_to_use}...")
                pyautogui.press('enter')
                time.sleep(1.0)
                pyautogui.press('enter')
                time.sleep(1.0)
                pyautogui.press('enter')
                print(f"[ANAY] WhatsApp message sent to number {num_to_use}")
                pyautogui.press('enter')
                return

            # CASE 2: Recipient is a name (GUI automation search)
            open_url("https://web.whatsapp.com")
            print(f"[ANAY] Waiting for WhatsApp Web to load to search for: {recipient}")
            time.sleep(12)
            
            # Focus search bar
            for _ in range(3):
                pyautogui.press('esc')
                time.sleep(0.2)
            
            pyautogui.hotkey('ctrl', 'alt', '/') 
            time.sleep(1.5)
            
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(1.0)
            
            print(f"[ANAY] Typing contact name: {recipient}")
            pyautogui.write(recipient, interval=0.15)
            time.sleep(4.0)
            
            pyautogui.press('down')
            time.sleep(0.8)
            pyautogui.press('enter')
            time.sleep(3.0)
            
            print(f"[ANAY] Typing message...")
            pyautogui.write(message, interval=0.1)
            time.sleep(1.5)
            pyautogui.press('enter')
            time.sleep(1.0)
            pyautogui.press('enter')
            print(f"[ANAY] WhatsApp message sent to {recipient}")
            
        except Exception as e:
            print(f"[ANAY] WhatsApp background error: {e}")

    # Run in background to avoid API timeout
    import threading
    threading.Thread(target=_send_logic, daemon=True).start()
    
    return f"WhatsApp message {recipient} ko bhej raha hoon background mein... 🙄"

def bluetooth_on() -> str:
    """Turn Bluetooth ON using PowerShell"""
    script = """
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $radios = [Windows.Devices.Radios.Radio, Windows.Devices.Radios, ContentType=WindowsRuntime]::GetRadiosAsync()
    while ($radios.Status -eq 'Started') { Start-Sleep -m 50 }
    $btRadio = $radios.GetResults() | Where-Object { $_.Kind -eq 'Bluetooth' }
    if ($btRadio) {
        $op = $btRadio.SetStateAsync([Windows.Devices.Radios.RadioState]::On)
        while ($op.Status -eq 'Started') { Start-Sleep -m 50 }
        Write-Output "ON"
    } else { Write-Output "NOT_FOUND" }
    """
    result = subprocess.run(["powershell","-Command",script], capture_output=True, text=True, timeout=15)
    if "ON" in result.stdout:
        return "Bluetooth ON kar diya! 🫡"
    # Fallback: open quick settings
    subprocess.run("start ms-settings:bluetooth", shell=True)
    return "Bluetooth hardware access limited, settings khol di hain. Wahan se ON kar le! 🙄"

def bluetooth_off() -> str:
    """Turn Bluetooth OFF using PowerShell"""
    script = """
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $radios = [Windows.Devices.Radios.Radio, Windows.Devices.Radios, ContentType=WindowsRuntime]::GetRadiosAsync()
    while ($radios.Status -eq 'Started') { Start-Sleep -m 50 }
    $btRadio = $radios.GetResults() | Where-Object { $_.Kind -eq 'Bluetooth' }
    if ($btRadio) {
        $op = $btRadio.SetStateAsync([Windows.Devices.Radios.RadioState]::Off)
        while ($op.Status -eq 'Started') { Start-Sleep -m 50 }
        Write-Output "OFF"
    }
    """
    subprocess.run(["powershell","-Command",script], capture_output=True, timeout=15)
    return "Bluetooth OFF kar diya! 🫡"

def bluetooth_status() -> str:
    script = """
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $radios = [Windows.Devices.Radios.Radio, Windows.Devices.Radios, ContentType=WindowsRuntime]::GetRadiosAsync()
    while ($radios.Status -eq 'Started') { Start-Sleep -m 50 }
    $btRadio = $radios.GetResults() | Where-Object { $_.Kind -eq 'Bluetooth' }
    if ($btRadio) { Write-Output $btRadio.State } else { Write-Output "Not found" }
    """
    result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, timeout=10)
    status = result.stdout.strip()
    return f"Bluetooth status: {status if status else 'Unknown'}"

def wifi_on() -> str:
    subprocess.run(
        ["netsh", "interface", "set", "interface", "Wi-Fi", "enable"],
        capture_output=True, text=True
    )
    return "WiFi ON kar diya! 🫡"

def wifi_off() -> str:
    subprocess.run(
        ["netsh", "interface", "set", "interface", "Wi-Fi", "disable"],
        capture_output=True
    )
    return "WiFi OFF kar diya! 🫡"

def set_brightness(level: int) -> str:
    """Set screen brightness 0-100"""
    script = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
    result = subprocess.run(
        ["powershell", "-Command", script],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return f"Brightness {level}% kar di! 🫡"
    return f"Brightness change failed (laptop display required): {result.stderr}"

def night_mode_on() -> str:
    subprocess.run(
        ["powershell", "-Command", "Start-Process 'ms-settings:nightlight'"],
        capture_output=True
    )
    return "Night mode settings khol di hain! 🙄"

def execute_tool(name: str, args: Dict[str, Any]) -> Any:
    """Unified executor for tools with argument filtering"""
    fn = TOOL_MAP.get(name)
    if not fn:
        return f"Tool '{name}' not found"
    
    try:
        # Get function signature to filter unexpected LLM arguments (hallucinations)
        sig = inspect.signature(fn)
        # If the function accepts **kwargs, we don't need to filter
        has_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
        
        if not has_kwargs:
            # Only pass keys that exist in the function's parameters
            valid_args = {k: v for k, v in args.items() if k in sig.parameters}
            if len(valid_args) < len(args):
                logger.warning(f"Filtered arguments for {name}: {set(args.keys()) - set(valid_args.keys())} dropped.")
            return fn(**valid_args)
        
        return fn(**args)
    except Exception as e:
        if 'logger' in globals() or 'logger' in locals():
            logger.error(f"Error executing tool {name}: {e}")
        else:
            print(f"[ERROR] Tool {name} failed: {e}")
        return f"Tool execution failed: {e}"

# Map used by router/main
TOOL_MAP = {
    "open_app":             open_app,
    "close_app":            close_app,
    "open_url":             open_url,
    "play_media":           play_media,
    "play_youtube_automated": play_youtube_automated,
    "type_text":            type_text,
    "click_mouse":          click_mouse,
    "move_mouse":           move_mouse,
    "scroll_mouse":         scroll_mouse,
    "scroll":               scroll,
    "click_at":             click_at,
    "search_web":           search_web,
    "move_file":            move_file,
    "delete_file":          delete_local_file,
    "read_file":            read_text_file,
    "write_file":           write_text_file,
    "send_email":           send_email,
    "send_whatsapp":        send_whatsapp,
    "set_reminder":         set_reminder,
    "run_terminal_command": run_terminal_command,
    "get_system_stats":     get_system_stats,
    "take_screenshot":      take_screenshot,
    "read_clipboard":       read_clipboard,
    "write_clipboard":      write_clipboard,
    "list_running_apps":    list_running_apps,
    "list_apps":            list_apps,
    "set_volume":           set_volume,
    "volume_up":            volume_up,
    "volume_down":          volume_down,
    "mute_volume":          mute_volume,
    "get_volume":           get_volume,
    "bluetooth_on":         bluetooth_on,
    "bluetooth_off":        bluetooth_off,
    "bluetooth_status":     bluetooth_status,
    "wifi_on":              wifi_on,
    "wifi_off":             wifi_off,
    "set_brightness":       set_brightness,
    "night_mode_on":        night_mode_on,
    "lock_screen":          lock_screen,
    "shutdown_pc":          shutdown_pc,
    "shutdown":             shutdown_pc,
    "restart":              restart_pc,
    "open_youtube":         open_youtube,
    "focus_window":         focus_window,
    "save_user_fact":       save_user_fact,
    "save_important_memory": save_important_memory,
    "save_contact":         save_contact,
}
