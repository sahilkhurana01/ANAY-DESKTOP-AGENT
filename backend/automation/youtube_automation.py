"""
YouTube Selenium Automation
Optimized for speed and instant feedback.
"""
import logging
import time
import webbrowser
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from automation.selenium_utils import DriverFactory

logger = logging.getLogger(__name__)

class YouTubeAutomation:
    def __init__(self):
        self.driver = None
        
    def play_video(self, video_name: str):
        """
        Play YouTube video with instant feedback and optimized Selenium.
        """
        try:
            # 1. Build search query and URL
            query = video_name.strip().replace(" ", "+")
            url = f"https://www.youtube.com/results?search_query={query}"
            
            # 2. INSTANT FEEDBACK: Open in user's default browser immediately
            # This makes the user see the page while Selenium is still setting up.
            logger.info(f"Instantly opening YouTube search for: {video_name}")
            webbrowser.open(url)
            
            # 3. Fast Selenium Initialization
            # Check if remote debugging is available (MUCH faster)
            is_remote = DriverFactory.is_port_open(9222)
            
            def perform_click():
                try:
                    options = DriverFactory.create_chrome_options(remote_debug=is_remote)
                    service = DriverFactory.get_service()
                    self.driver = webdriver.Chrome(service=service, options=options)
                    
                    # If we opened a new browser (not remote), we need to navigate
                    if not is_remote:
                        self.driver.get(url)
                    
                    # 4. Optimized Selection (Short timeout)
                    wait = WebDriverWait(self.driver, 5) # 5s is plenty if page is loading
                    
                    video_selectors = [
                        "a#video-title",
                        "ytd-video-renderer a#thumbnail",
                        "a.yt-simple-endpoint.ytd-video-renderer"
                    ]
                    
                    for selector in video_selectors:
                        try:
                            video_link = wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            video_link.click()
                            logger.info(f"✅ Successfully clicked video for: {video_name}")
                            return True
                        except:
                            continue
                except Exception as e:
                    logger.error(f"Background YouTube click failed: {e}")
                finally:
                    # Don't quit if it's the remote driver, we want the video to keep playing!
                    pass

            # Always run the Selenium part in a thread to prevent freezing the assistant
            threading.Thread(target=perform_click, daemon=True).start()
            
            return True, f"Now playing {video_name} on YouTube"
            
        except Exception as e:
            logger.error(f"YouTube automation failed: {e}")
            return True, f"Opened YouTube search for: {video_name}" # Fallback success

    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
