import os
import socket
import logging
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class DriverFactory:
    _instance = None
    _lock = threading.Lock()
    _driver_path = None
    _service = None

    @classmethod
    def get_driver_path(cls):
        with cls._lock:
            if not cls._driver_path:
                logger.info("Installing/Locating ChromeDriver...")
                cls._driver_path = ChromeDriverManager().install()
            return cls._driver_path

    @classmethod
    def get_service(cls):
        with cls._lock:
            if not cls._service:
                path = cls.get_driver_path()
                cls._service = Service(path)
            return cls._service

    @staticmethod
    def is_port_open(port=9222):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    @classmethod
    def create_chrome_options(cls, remote_debug=True, headless=False):
        options = webdriver.ChromeOptions()
        
        # Detect Browser Binary
        brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        
        if os.path.exists(brave_path):
            options.binary_location = brave_path
        elif os.path.exists(chrome_path):
            options.binary_location = chrome_path
        
        if remote_debug and cls.is_port_open(9222):
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        else:
            # Add arguments to make it faster/stable if launching new
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--start-maximized")
            if headless:
                options.add_argument("--headless")
            
            # Use a persistent user data dir to keep logins
            user_data_dir = os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\User Data Selenium")
            options.add_argument(f"user-data-dir={user_data_dir}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
        return options
