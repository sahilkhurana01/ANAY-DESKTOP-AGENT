"""
Sarvam AI Text-to-Speech Streaming Module
Mimics streaming interface using Sarvam AI REST API
"""
import os
import asyncio
import logging
import base64
try:
    import aiohttp
except ImportError:
    aiohttp = None
import json
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


class SarvamStreamer:
    """Handles text-to-speech using Sarvam AI API with a streaming-compatible interface."""
    
    def __init__(self, api_key: str, speaker: str = "kabir"):
        """
        Initialize Sarvam streamer.
        
        Args:
            api_key: Sarvam AI API key
            speaker: Speaker name (default: kabir)
        """
        self.api_key = api_key
        self.speaker = speaker or "kabir"
        self.model_id = "bulbul:v3"
        self.base_url = "https://api.sarvam.ai/text-to-speech"
        
        logger.info(f"Sarvam Streamer initialized (Speaker: {self.speaker})")

    async def stream_text(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Convert text to speech and yield audio chunks.
        Even though we use REST, we yield in chunks to maintain interface compatibility.
        
        Args:
            text: Text to convert to speech
            
        Yields:
            Audio bytes chunks (MP3 format)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS")
            return
            
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": [text],
            "target_language_code": "hi-IN", # Default to hindi/hinglish context
            "speaker": self.speaker,
            "model": self.model_id,
            "speech_sample_rate": 24000,
            "output_audio_codec": "mp3"
        }
        
        try:
            if aiohttp is None:
                logger.error("aiohttp package not installed. Skipping synthesis.")
                return
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=data, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise RuntimeError(
                            f"Sarvam AI API error {response.status}: {error_text[:1200]}"
                        )
                    
                    result = await response.json()
                    if not result or 'audios' not in result or not result['audios']:
                        return

                    audio_base64 = result['audios'][0]
                    audio_bytes = base64.b64decode(audio_base64)
                    
                    # Yield audio in chunks to reduce buffering impact in the consumer
                    chunk_size = 65536
                    for i in range(0, len(audio_bytes), chunk_size):
                        yield audio_bytes[i:i+chunk_size]
                        # Minor sleep to avoid saturating the local socket immediately
                        await asyncio.sleep(0.01)
                            
            logger.info(f"Sarvam TTS synthesis completed for: {text[:50]}...")
            
        except aiohttp.ClientError as e:
            logger.error("HTTP error during Sarvam TTS: %s", e)
            raise
        except Exception as e:
            logger.error("Sarvam TTS streaming failed: %s", e)
            raise

    async def synthesize_full(self, text: str) -> bytes:
        """
        Synthesize full audio for text.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Complete audio bytes (MP3 format)
        """
        chunks = []
        async for chunk in self.stream_text(text):
            chunks.append(chunk)
        return b''.join(chunks)
