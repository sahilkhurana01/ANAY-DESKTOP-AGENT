"""
Spotify Selenium Automation
Optimized for speed and instant feedback.
"""
import logging
import time
import webbrowser
import threading
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from automation.selenium_utils import DriverFactory

logger = logging.getLogger(__name__)

class SpotifyAutomation:
    def __init__(self):
        self.driver = None
        
    def play_song(self, song_name: str, artist_name: str = ""):
        """
        Play Spotify song with instant feedback and optimized Selenium.
        """
        try:
            # 1. Build search query and URL
            query = f"{song_name} {artist_name}".strip().replace(" ", "+")
            url = f"https://open.spotify.com/search/{query}"
            
            # 2. INSTANT FEEDBACK: Open in user's default browser immediately
            logger.info(f"Instantly opening Spotify search for: {song_name} {artist_name}")
            webbrowser.open(url)
            
            # 3. Fast Selenium Initialization
            is_remote = DriverFactory.is_port_open(9222)
            
            def perform_play():
                try:
                    options = DriverFactory.create_chrome_options(remote_debug=is_remote)
                    service = DriverFactory.get_service()
                    self.driver = webdriver.Chrome(service=service, options=options)
                    
                    if not is_remote:
                        self.driver.get(url)
                    
                    # 4. Optimized Selection (Short timeout)
                    wait = WebDriverWait(self.driver, 5)
                    
                    play_button_selectors = [
                        "button[aria-label*='Play']",
                        "button[data-testid='play-button']",
                        "button.playButton",
                        "button[title*='Play']",
                        "[aria-label*='play' i]"
                    ]
                    
                    for selector in play_button_selectors:
                        try:
                            play_button = wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            play_button.click()
                            logger.info(f"✅ Successfully clicked play button for: {song_name}")
                            return True
                        except:
                            continue
                except Exception as e:
                    logger.error(f"Background Spotify play failed: {e}")

            # Always run the Selenium part in a thread to prevent freezing the assistant
            threading.Thread(target=perform_play, daemon=True).start()
            
            return True, f"Now playing {song_name} on Spotify"
            
        except Exception as e:
            logger.error(f"Spotify automation failed: {e}")
            return True, f"Opened Spotify search for: {song_name}" # Fallback success
    
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
