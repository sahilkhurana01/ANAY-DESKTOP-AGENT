"""
Text-to-Speech Module
Converts text to speech using Sarvam AI API
"""
import os
import logging
import requests
import base64
from pathlib import Path

logger = logging.getLogger(__name__)

class TextToSpeech:
    """Converts text to speech audio using Sarvam AI (Bulbul) API."""
    
    def __init__(
        self,
        api_key: str = None,
        speaker: str = "kabir"
    ):
        """
        Initialize Sarvam AI TTS client.
        
        Args:
            api_key: Sarvam AI API key (defaults to config)
            speaker: Speaker name (default: kabir)
        """
        from config import SARVAM_API_KEY
        self.api_key = api_key or SARVAM_API_KEY
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY not found. Please set it in api.txt or environment.")
        
        self.speaker = speaker or "kabir"
        self.base_url = "https://api.sarvam.ai/text-to-speech"
        
        logger.info(f"Sarvam AI TTS initialized (Speaker: {self.speaker})")
    
    def synthesize(
        self,
        text: str,
        output_path: str,
        language_code: str = "hi-IN"
    ) -> str:
        """
        Convert text to speech and save as audio file.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file (MP3/WAV)
            language_code: BCP-47 language code (default hi-IN)
            
        Returns:
            Path to saved audio file
        """
        try:
            logger.info(f"Synthesizing speech with Sarvam AI: {text[:50]}...")
            
            headers = {
                "api-subscription-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "inputs": [text],
                "target_language_code": language_code,
                "speaker": self.speaker,
                "model": "bulbul:v3",
                "speech_sample_rate": 24000,
                "output_audio_codec": "mp3"
            }
            
            # Make API request
            response = requests.post(self.base_url, json=data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if not result or 'audios' not in result or not result['audios']:
                raise ValueError("No audio content returned from Sarvam AI")
                
            # Sarvam returns audio as base64 list
            audio_base64 = result['audios'][0]
            audio_bytes = base64.b64decode(audio_base64)
            
            # Save audio file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            logger.info(f"Audio saved to {output_path}")
            return str(output_path)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Sarvam AI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise
    
    def get_available_voices(self) -> list:
        """
        List of common Sarvam AI voices.
        """
        # Sarvam doesn't have a simple REST endpoint to list voices yet in the same way ElevenLabs did,
        # but we know the popular ones from the docs.
        return [
            {"voice_id": "kabir", "name": "Kabir (Male)", "category": "v3"},
            {"voice_id": "arvind", "name": "Arvind (Male)", "category": "v3"},
            {"voice_id": "meera", "name": "Meera (Female)", "category": "v3"},
        ]


if __name__ == "__main__":
    # Test TTS
    logging.basicConfig(level=logging.INFO)
    from config import SARVAM_API_KEY
    
    tts = TextToSpeech(api_key=SARVAM_API_KEY)
    
    test_text = "नमस्ते! मैं ANAY हूं, आपका AI सहायक।"
    output_file = "test_sarvam_output.mp3"
    
    print(f"Synthesizing: {test_text}")
    audio_path = tts.synthesize(test_text, output_file)
    print(f"Audio saved to: {audio_path}")
