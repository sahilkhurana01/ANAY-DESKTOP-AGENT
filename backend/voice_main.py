"""
ANAY Voice Assistant - Standalone Mode
Automatically listens and responds via voice
"""
import asyncio
import time
import logging
import os
import pyaudio
from speech_to_text import SpeechToText
from tts.sarvam_stream import SarvamStreamer
from llm_router import llm_router
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5

class VoiceAssistant:
    def __init__(self):
        self.stt = SpeechToText()
        self.router = llm_router
        self.tts = SarvamStreamer(os.getenv('SARVAM_API_KEY'), speaker="kabir")
        self.audio = pyaudio.PyAudio()
        
    def record_audio(self):
        """Record audio from microphone"""
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        logger.info("Listening...")
        frames = []
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        logger.info("Done listening")
        stream.stop_stream()
        stream.close()
        return b''.join(frames)
    
    async def process_voice_input(self):
        """Main voice processing loop"""
        while True:
            try:
                # Record audio
                audio_data = self.record_audio()
                
                # Transcribe
                logger.info("Transcribing...")
                transcript = self.stt.transcribe(audio_data)
                
                if not transcript or transcript.strip() == "":
                    continue
                    
                logger.info(f"You said: {transcript}")
                
                # Generate response using unified router
                response_start = time.time()
                result = self.router.chat(transcript)
                ai_response = result["text"]
                
                logger.info(f"ANAY: {ai_response}")
                
                if result.get("tool_calls"):
                    logger.info(f"Executed tools: {[tc['name'] for tc in result['tool_calls']]}")
                
                # Stream and play audio
                logger.info("Speaking...")
                audio_chunks = []
                async for chunk in self.tts.stream_text(ai_response):
                    audio_chunks.append(chunk)
                
                self.play_audio(b''.join(audio_chunks))
                
            except KeyboardInterrupt:
                logger.info("\nShutting down...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                continue
    
    def play_audio(self, audio_data):
        """Play audio through speakers"""
        stream = self.audio.open(
            format=FORMAT,
            channels=1,
            rate=24000, 
            output=True
        )
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()
    
    def cleanup(self):
        """Cleanup resources"""
        self.audio.terminate()

async def main():
    logger.info("=" * 50)
    logger.info("ANAY Voice Assistant - Standalone Mode")
    logger.info("=" * 50)
    logger.info("Press Ctrl+C to exit\n")
    
    assistant = VoiceAssistant()
    try:
        await assistant.process_voice_input()
    finally:
        assistant.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
