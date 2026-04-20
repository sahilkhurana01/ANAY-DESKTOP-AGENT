import os
import asyncio
import logging
from deepgram import DeepgramClient
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class DeepgramStreamer:
    """Handles real-time speech-to-text using Deepgram Streaming API."""
    
    def __init__(self, api_key: str, on_transcript: Callable[[str, bool], None]):
        """
        Initialize Deepgram client.
        on_transcript: callback(transcript, is_final)
        """
        self.api_key = api_key
        self.on_transcript = on_transcript
        # SDK v5.3.1 requires API key via environment variable
        os.environ['DEEPGRAM_API_KEY'] = api_key
        self.dg_client = DeepgramClient()
        self.dg_connection = None
        self.connection_context_manager = None
        
    async def start(self):
        """Start the Deepgram live connection."""
        try:
            # Create options for the connection
            options = {
                "model": "nova-2",
                "language": "en-US",
                "smart_format": True,
                "interim_results": True,
                "encoding": "linear16",
                "sample_rate": 16000,
            }
            
            # Use correct SDK v5.3.1 API - returns a context manager
            self.connection_context_manager = self.dg_client.listen.v1.connect(**options)
            self.dg_connection = await self.connection_context_manager.__aenter__()
            
            # Define event handlers
            def on_message(self, result, **kwargs):
                try:
                    sentence = result.channel.alternatives[0].transcript
                    if len(sentence) > 0:
                        is_final = result.is_final
                        # Call the callback directly (asyncio handling in websocket_manager)
                        asyncio.create_task(self.on_transcript(sentence, is_final))
                except Exception as e:
                    logger.error(f"Error processing transcript: {e}")

            def on_error(self, error, **kwargs):
                logger.error(f"Deepgram Error: {error}")
            
            # Register event handlers - use string event names instead of enums
            try:
                self.dg_connection.on("Results", on_message)
                self.dg_connection.on("Error", on_error)
            except Exception as e:
                logger.warning(f"Could not register event handlers: {e}")
                
            logger.info("Deepgram Live connection started.")
            
        except Exception as e:
            logger.error(f"Failed to start Deepgram connection: {e}")
            raise

    async def send_audio(self, audio_data: bytes):
        """Send raw audio bytes to Deepgram."""
        if self.dg_connection:
            await self.dg_connection.send(audio_data)

    async def stop(self):
        """Stop the Deepgram live connection."""
        if self.connection_context_manager and self.dg_connection:
            try:
                await self.connection_context_manager.__aexit__(None, None, None)
                logger.info("Deepgram Live connection stopped.")
            except Exception as e:
                logger.error(f"Error stopping Deepgram connection: {e}")
