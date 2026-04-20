import numpy as np
import base64
import logging

logger = logging.getLogger(__name__)

def calculate_amplitude(audio_base64: str) -> float:
    """
    Calculate the normalized amplitude (0.0 to 1.0) of base64 encoded PCM audio.
    Assumes 16-bit PCM mono.
    """
    try:
        audio_data = base64.b64decode(audio_base64)
        # Convert bytes to 16-bit integers
        samples = np.frombuffer(audio_data, dtype=np.int16)
        
        if len(samples) == 0:
            return 0.0
            
        # Calculate RMS (Root Mean Square)
        rms = np.sqrt(np.mean(samples.astype(np.float32)**2))
        
        # Max value for 16-bit PCM is 32768
        # Normalize to 0.0 - 1.0 range, adding some sensitivity
        normalized = min(1.0, rms / 16384.0)
        
        return float(normalized)
    except Exception as e:
        logger.error(f"Error calculating amplitude: {e}")
        return 0.0
