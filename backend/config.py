"""Configuration and environment variables for ANAY backend."""
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

# Read API keys from api.txt file
def read_api_keys():
    """Read API keys from api.txt file in the parent directory."""
    # Only try to read if not in production environment
    if os.getenv("RENDER") or os.getenv("ENV") == "production":
        return {}

    api_file = Path(__file__).parent.parent / "api.txt"
    api_keys = {}
    
    if api_file.exists():
        try:
            with open(api_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                    if key == "Deepgram":
                        api_keys['DEEPGRAM_API_KEY'] = value
                    elif key == "Eleven Labs":
                        api_keys['ELEVENLABS_API_KEY'] = value
                    elif key == "OpenAI":
                        api_keys['OPENAI_API_KEY'] = value
                    elif key == "Groq":
                        api_keys['GROQ_API_KEY'] = value
        except Exception as e:
            print(f"Warning: Could not read api.txt: {e}")
    
    return api_keys

# Load API keys from file
file_api_keys = read_api_keys()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or file_api_keys.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Deepgram STT Configuration
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY") or file_api_keys.get("DEEPGRAM_API_KEY", "")

# Sarvam AI TTS Configuration
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY") or file_api_keys.get("SARVAM_API_KEY", "")

# Server Configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", os.getenv("SERVER_PORT", "8000")))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8080,http://localhost:5173,https://anay-ai.onrender.com").split(",")

# AI Configuration
MAX_CONTEXT_MESSAGES = 20
DEFAULT_TEMPERATURE = 0.8
DEFAULT_MAX_TOKENS = 1024

# System Control Configuration
ALLOWED_FILE_EXTENSIONS = ['.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3', '.wav']
MAX_PATH_LENGTH = 500
