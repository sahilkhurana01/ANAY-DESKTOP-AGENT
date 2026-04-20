"""
Audio Output Module
Plays audio files using Pygame
"""
import os
import logging
import pygame
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class AudioPlayer:
    """Plays audio files using Pygame mixer."""
    
    def __init__(self, frequency: int = 44100, size: int = -16, channels: int = 2, buffer: int = 2048):
        """
        Initialize Pygame audio mixer.
        
        Args:
            frequency: Audio frequency (Hz)
            size: Sample size
            channels: Number of audio channels (1=mono, 2=stereo)
            buffer: Buffer size
        """
        try:
            pygame.mixer.init(frequency=frequency, size=size, channels=channels, buffer=buffer)
            logger.info("Pygame audio mixer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Pygame mixer: {e}")
            raise
    
    def play(self, audio_path: str, blocking: bool = True):
        """
        Play an audio file.
        
        Args:
            audio_path: Path to audio file (WAV or MP3)
            blocking: If True, wait for playback to finish
        """
        try:
            audio_path = Path(audio_path)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            logger.info(f"Playing audio: {audio_path}")
            
            # Load and play audio
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.play()
            
            # Wait for playback to finish if blocking
            if blocking:
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                logger.info("Playback finished")
            else:
                logger.info("Playback started (non-blocking)")
                
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
            raise
    
    def stop(self):
        """Stop current audio playback."""
        try:
            pygame.mixer.music.stop()
            logger.info("Audio playback stopped")
        except Exception as e:
            logger.error(f"Failed to stop playback: {e}")
    
    def pause(self):
        """Pause current audio playback."""
        try:
            pygame.mixer.music.pause()
            logger.info("Audio playback paused")
        except Exception as e:
            logger.error(f"Failed to pause playback: {e}")
    
    def resume(self):
        """Resume paused audio playback."""
        try:
            pygame.mixer.music.unpause()
            logger.info("Audio playback resumed")
        except Exception as e:
            logger.error(f"Failed to resume playback: {e}")
    
    def set_volume(self, volume: float):
        """
        Set playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        try:
            volume = max(0.0, min(1.0, volume))  # Clamp to 0.0-1.0
            pygame.mixer.music.set_volume(volume)
            logger.info(f"Volume set to {volume}")
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
    
    def is_playing(self) -> bool:
        """
        Check if audio is currently playing.
        
        Returns:
            True if audio is playing, False otherwise
        """
        return pygame.mixer.music.get_busy()
    
    def cleanup(self):
        """Clean up Pygame mixer resources."""
        try:
            pygame.mixer.quit()
            logger.info("Pygame mixer cleaned up")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


if __name__ == "__main__":
    # Test audio player
    logging.basicConfig(level=logging.INFO)
    
    with AudioPlayer() as player:
        test_file = "test_tts_output.mp3"
        if Path(test_file).exists():
            print(f"Playing: {test_file}")
            player.play(test_file, blocking=True)
        else:
            print(f"Test audio file not found: {test_file}")
