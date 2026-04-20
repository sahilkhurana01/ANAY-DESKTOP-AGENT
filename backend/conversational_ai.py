"""
Conversational AI Assistant
Implements the complete pipeline from the flowchart:
1. PyAudio → Record .wav
2. Deepgram API → Transcript
3. OpenAI API → Response
4. Eleven Labs API → Speech .wav
5. Pygame → Output

This implements a talkback function for continuous conversation.
"""
import logging
import time
import tempfile
from pathlib import Path
from typing import Optional

from audio_input import AudioRecorder
from speech_to_text import SpeechToText
from groq_llm import GroqLLM
from text_to_speech import TextToSpeech
from audio_output import AudioPlayer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConversationalAI:
    """
    Main conversational AI assistant that implements the complete pipeline.
    Follows the exact hierarchy from the flowchart.
    """
    
    def __init__(
        self,
        record_duration: float = 5.0,
        sample_rate: int = 16000,
        language: str = "en"
    ):
        """
        Initialize the conversational AI assistant.
        
        Args:
            record_duration: How long to record audio in seconds
            sample_rate: Audio sample rate (Hz)
            language: Language for transcription (en/hi)
        """
        self.record_duration = record_duration
        self.sample_rate = sample_rate
        self.language = language
        
        # Initialize components
        logger.info("Initializing Conversational AI components...")
        
        # 1. Audio Input (PyAudio)
        self.audio_recorder = AudioRecorder(
            sample_rate=sample_rate,
            channels=1,
            chunk_size=1024
        )
        
        # 2. Speech-to-Text (Deepgram API)
        self.stt = SpeechToText()
        
        # 3. AI Processing (Groq API)
        self.active_llm = GroqLLM()
        
        # 4. Text-to-Speech (Eleven Labs API)
        self.tts = TextToSpeech()
        
        # 5. Audio Output (Pygame)
        self.audio_player = AudioPlayer()
        
        logger.info("All components initialized successfully!")
    
    def process_conversation_cycle(self) -> bool:
        """
        Process one complete conversation cycle following the flowchart.
        
        Returns:
            True if conversation should continue, False to exit
        """
        try:
            # Step 1: Record audio using PyAudio
            logger.info("=" * 60)
            logger.info("🎤 Step 1: Recording audio (PyAudio)...")
            logger.info(f"Recording for {self.record_duration} seconds...")
            
            # Create temporary file for recording
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_wav_path = temp_wav.name
            temp_wav.close()
            
            # Initialize temp_speech_path for cleanup
            temp_speech_path = None
            
            try:
                # Record audio
                with self.audio_recorder:
                    recorded_file = self.audio_recorder.record(
                        duration=self.record_duration,
                        output_path=temp_wav_path
                    )
                
                logger.info(f"✅ Audio recorded: {recorded_file}")
                
                # Step 2: Transcribe using Deepgram API
                logger.info("📝 Step 2: Transcribing audio (Deepgram API)...")
                transcript_start = time.time()
                
                transcript = self.stt.transcribe(recorded_file, language=self.language)
                transcript_time = time.time() - transcript_start
                
                if not transcript or transcript.strip() == "":
                    logger.warning("⚠️  No speech detected in audio")
                    return True  # Continue listening
                
                logger.info(f"✅ Transcription complete ({transcript_time:.2f}s): {transcript}")
                
                # Step 3: Generate AI response using Gemini API
                logger.info("🤖 Step 3: Generating AI response (Gemini API)...")
                response_start = time.time()
                
                ai_response = self.active_llm.generate_response(transcript)
                response_time = time.time() - response_start
                
                logger.info(f"✅ Response generated ({response_time:.2f}s): {ai_response[:100]}...")
                
                # Step 4: Convert to speech using Eleven Labs API
                logger.info("🔊 Step 4: Converting to speech (Eleven Labs API)...")
                tts_start = time.time()
                
                # Create temporary file for TTS output
                temp_speech = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                temp_speech_path = temp_speech.name
                temp_speech.close()
                
                # Use high-quality voice settings
                speech_file = self.tts.synthesize(
                    text=ai_response,
                    output_path=temp_speech_path,
                    stability=0.5,  # Balanced stability
                    similarity_boost=0.75,  # High similarity for natural voice
                    style=0.0,  # Neutral style
                    use_speaker_boost=True  # Enhanced clarity
                )
                tts_time = time.time() - tts_start
                
                logger.info(f"✅ Speech generated ({tts_time:.2f}s): {speech_file}")
                
                # Step 5: Play audio using Pygame
                logger.info("🔊 Step 5: Playing audio (Pygame)...")
                logger.info("🗣️  ANAY: " + ai_response)
                
                with self.audio_player:
                    self.audio_player.play(speech_file, blocking=True)
                
                logger.info("✅ Audio playback complete")
                logger.info("=" * 60)
                
                return True  # Continue conversation
                
            finally:
                # Clean up temporary files
                try:
                    if temp_wav_path and Path(temp_wav_path).exists():
                        Path(temp_wav_path).unlink(missing_ok=True)
                except:
                    pass
                try:
                    if temp_speech_path and Path(temp_speech_path).exists():
                        Path(temp_speech_path).unlink(missing_ok=True)
                except:
                    pass
                    
        except KeyboardInterrupt:
            logger.info("\n⚠️  Interrupted by user")
            return False
        except Exception as e:
            logger.error(f"❌ Error in conversation cycle: {e}", exc_info=True)
            return True  # Continue despite errors
    
    def start_conversation(self):
        """
        Start the conversational AI assistant with talkback functionality.
        Runs continuously until interrupted.
        """
        logger.info("=" * 60)
        logger.info("🚀 ANAY Conversational AI Assistant")
        logger.info("=" * 60)
        logger.info("Following the complete pipeline:")
        logger.info("  1. PyAudio → Record .wav")
        logger.info("  2. Deepgram API → Transcript")
        logger.info("  3. Groq API → Response")
        logger.info("  4. Eleven Labs API → Speech .wav")
        logger.info("  5. Pygame → Output")
        logger.info("=" * 60)
        logger.info("Press Ctrl+C to exit\n")
        
        try:
            while True:
                should_continue = self.process_conversation_cycle()
                if not should_continue:
                    break
                
                # Small delay between cycles
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            logger.info("\n👋 Shutting down ANAY assistant...")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up all resources."""
        logger.info("Cleaning up resources...")
        try:
            if hasattr(self, 'audio_recorder'):
                self.audio_recorder.stop()
        except:
            pass
        try:
            if hasattr(self, 'audio_player'):
                self.audio_player.cleanup()
        except:
            pass
        logger.info("Cleanup complete")


def main():
    """Main entry point for the conversational AI assistant."""
    # Create and start the assistant
    assistant = ConversationalAI(
        record_duration=5.0,  # Record for 5 seconds
        sample_rate=16000,   # 16kHz sample rate
        language="en"        # English (change to "hi" for Hindi)
    )
    
    assistant.start_conversation()


if __name__ == "__main__":
    main()
