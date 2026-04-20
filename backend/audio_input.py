"""
Audio Input Module
Handles microphone recording using PyAudio
"""
import pyaudio
import wave
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AudioRecorder:
    """Records audio from microphone and saves to WAV file."""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        format: int = pyaudio.paInt16
    ):
        """
        Initialize audio recorder.
        
        Args:
            sample_rate: Audio sample rate (Hz)
            channels: Number of audio channels
            chunk_size: Buffer size for recording
            format: PyAudio format
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = format
        self.audio = None
        self.stream = None
        
    def start(self):
        """Initialize PyAudio and open audio stream."""
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            logger.info("Audio stream started successfully")
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            raise
    
    def record(self, duration: float, output_path: str) -> str:
        """
        Record audio for specified duration and save to file.
        
        Args:
            duration: Recording duration in seconds
            output_path: Path to save WAV file
            
        Returns:
            Path to saved audio file
        """
        if not self.stream:
            raise RuntimeError("Audio stream not started. Call start() first.")
        
        try:
            logger.info(f"Recording for {duration} seconds...")
            frames = []
            
            # Calculate number of chunks to record
            chunks_to_record = int(self.sample_rate / self.chunk_size * duration)
            
            # Record audio
            for _ in range(chunks_to_record):
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
            
            logger.info("Recording complete, saving to file...")
            
            # Save to WAV file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with wave.open(str(output_path), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            logger.info(f"Audio saved to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            raise
    
    def stop(self):
        """Close audio stream and terminate PyAudio."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                logger.info("Audio stream closed")
            
            if self.audio:
                self.audio.terminate()
                logger.info("PyAudio terminated")
                
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


if __name__ == "__main__":
    # Test the audio recorder
    logging.basicConfig(level=logging.INFO)
    
    with AudioRecorder() as recorder:
        print("Recording for 3 seconds...")
        audio_file = recorder.record(duration=3.0, output_path="test_recording.wav")
        print(f"Recording saved to: {audio_file}")
