"""
Audio Format Converter
Converts webm audio to wav format for Deepgram compatibility
"""
import logging
import tempfile
import subprocess
import os
import wave
import struct
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

def convert_webm_to_wav(webm_path: str) -> str:
    """
    Convert webm audio file to wav format using multiple methods.
    
    Args:
        webm_path: Path to webm audio file
        
    Returns:
        Path to converted wav file (or original if conversion fails)
    """
    # Create temporary wav file
    wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    wav_path = wav_file.name
    wav_file.close()
    
    # Method 1: Try using PyAV (av library) - no external dependencies needed
    try:
        import av
        container = av.open(webm_path)
        if len(container.streams.audio) == 0:
            raise ValueError("No audio stream found")
        
        stream = container.streams.audio[0]
        logger.info(f"PyAV: Found audio stream, rate={stream.rate}, channels={stream.channels}")
        
        # Open output WAV file
        with wave.open(wav_path, 'wb') as wav_out:
            wav_out.setnchannels(1)  # Mono
            wav_out.setsampwidth(2)   # 16-bit
            wav_out.setframerate(16000)  # 16kHz
            
            # Create resampler if needed
            resampler = None
            if stream.rate != 16000 or stream.channels != 1:
                resampler = av.AudioResampler(rate=16000, layout='mono', format='s16')
            
            frame_count = 0
            # Decode and write audio frames
            for frame in container.decode(stream):
                frame_count += 1
                # Resample to 16kHz mono if needed
                if resampler:
                    frame.pts = None
                    resampled_frames = resampler.resample(frame)
                else:
                    resampled_frames = [frame]
                
                # Convert each resampled frame to bytes and write
                for resampled_frame in resampled_frames:
                    audio_data = resampled_frame.to_ndarray()
                    if audio_data.ndim > 1:
                        audio_data = audio_data[0]  # Take first channel
                    
                    # Convert to int16
                    if audio_data.dtype in ['float32', 'float64']:
                        # Clamp values to [-1, 1] range
                        audio_data = np.clip(audio_data, -1.0, 1.0)
                        audio_data = (audio_data * 32767).astype('int16')
                    elif audio_data.dtype != 'int16':
                        audio_data = audio_data.astype('int16')
                    
                    wav_out.writeframes(audio_data.tobytes())
        
        container.close()
        
        if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            logger.info(f"✅ Converted {webm_path} to {wav_path} using PyAV ({frame_count} frames)")
            return wav_path
        else:
            raise ValueError("Conversion produced empty file")
    except ImportError:
        logger.debug("PyAV (av) not available, trying other methods")
    except Exception as e:
        logger.warning(f"PyAV conversion failed: {e}, trying other methods")
        import traceback
        logger.debug(traceback.format_exc())
    
    # Method 2: Try using pydub (requires ffmpeg)
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(webm_path, format="webm")
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_path, format="wav")
        if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            logger.info(f"Converted {webm_path} to {wav_path} using pydub")
            return wav_path
    except ImportError:
        logger.debug("pydub not available")
    except Exception as e:
        logger.debug(f"pydub conversion failed: {e}")
    
    # Method 3: Try using ffmpeg directly
    try:
        result = subprocess.run(
            [
                'ffmpeg', '-i', webm_path,
                '-ar', '16000',
                '-ac', '1',
                '-f', 'wav',
                '-y',
                wav_path
            ],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            logger.info(f"Converted {webm_path} to {wav_path} using ffmpeg")
            return wav_path
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        logger.debug(f"ffmpeg conversion failed: {e}")
    
    # Clean up failed wav file
    try:
        if os.path.exists(wav_path):
            os.unlink(wav_path)
    except:
        pass
    
    logger.warning(f"Could not convert {webm_path}, will try direct webm")
    return webm_path
