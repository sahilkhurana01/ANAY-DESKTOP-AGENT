# ANAY Backend - Voice-Based AI Assistant

## 🎯 Overview

Production-ready Python backend for ANAY, a voice-based personal AI assistant that:
- Listens to your voice
- Converts speech to text (Deepgram)
- Processes with AI (Google Gemini)
- Executes system commands
- Responds with natural voice (ElevenLabs)

## 🏗️ Architecture

**Complete Pipeline:**
```
Microphone → PyAudio → Deepgram STT → Gemini LLM → ElevenLabs TTS → Pygame → Speaker
```

**Modules:**
- `audio_input.py` - Microphone recording
- `speech_to_text.py` - Deepgram integration
- `gemini_llm.py` - Google Gemini AI
- `memory.py` - Conversation context
- `text_to_speech.py` - Eleven Labs TTS
- `audio_output.py` - Pygame audio playback
- `command_router.py` - System command execution
- `voice_main.py` - Standalone voice mode
- `main.py` - FastAPI web server (for frontend)

## 📋 Prerequisites

- Python 3.10+
- Windows OS (primary support)
- Microphone and speakers
- API Keys:
  - Deepgram API
  - Google Gemini API
  - ElevenLabs API

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```env
DEEPGRAM_API_KEY=your_deepgram_key
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

### 3. Run Standalone Voice Mode

```bash
python voice_main.py
```

Say "exit" or "goodbye" to stop.

### 4. Run Web Server Mode (with Frontend)

```bash
python main.py
```

Then open `http://localhost:8080` in your browser.

## 🎮 Usage

### Standalone Voice Mode

```python
from voice_main import VoiceAssistant

assistant = VoiceAssistant()
assistant.run_conversation_loop()
```

### Individual Modules

```python
# Record audio
from audio_input import AudioRecorder
recorder = AudioRecorder()
recorder.start()
audio_file = recorder.record(duration=5.0, output_path="recording.wav")
recorder.stop()

# Transcribe
from speech_to_text import SpeechToText
stt = SpeechToText()
text = stt.transcribe("recording.wav")

# Get AI response
from gemini_llm import GeminiLLM
llm = GeminiLLM()
response = llm.generate_response(text)

# Convert to speech
from text_to_speech import TextToSpeech
tts = TextToSpeech()
audio = tts.synthesize(response, "response.mp3")

# Play audio
from audio_output import AudioPlayer
player = AudioPlayer()
player.play(audio)
```

## ⚙️ System Commands

ANAY can execute system commands:

- **"Open Chrome"** - Launches Chrome browser
- **"Open Calculator"** - Opens calculator
- **"Open Downloads folder"** - Opens Downloads
- **"Open Documents"** - Opens Documents folder

Commands are detected via `command_router.py`.

## 🧠 Conversation Memory

The assistant remembers recent conversation context (last 10 message pairs by default).

```python
from memory import ConversationMemory

memory = ConversationMemory(max_messages=10)
memory.add_user_message("Hello")
memory.add_assistant_message("Hi there!")
context = memory.get_context()
```

## 🔧 Configuration

### Audio Settings

```python
recorder = AudioRecorder(
    sample_rate=16000,  # Hz
    channels=1,         # Mono
    chunk_size=1024     # Buffer size
)
```

### TTS Voice Settings

```python
tts = TextToSpeech(
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
)

tts.synthesize(
    text="Hello",
    output_path="output.mp3",
    stability=0.5,
    similarity_boost=0.75
)
```

## 🌐 Web Integration

The backend includes FastAPI endpoints for the React frontend:

- WebSocket: `ws://localhost:8000/ws`
- Health check: `http://localhost:8000/health`
- System metrics: Broadcasted every 2 seconds

## 📁 Project Structure

```
backend/
├── audio_input.py          # Microphone recording
├── speech_to_text.py       # Deepgram STT
├── gemini_llm.py           # Gemini AI
├── memory.py               # Conversation memory
├── text_to_speech.py       # ElevenLabs TTS
├── audio_output.py         # Pygame playback
├── command_router.py       # Command execution
├── voice_main.py           # Standalone entry point
├── main.py                 # FastAPI server
├── websocket_manager.py    # WebSocket handler
├── system_monitor.py       # System metrics
├── requirements.txt        # Dependencies
├── .env                    # API keys (create from .env.example)
└── temp_audio/             # Temporary audio files
```

## 🐛 Troubleshooting

### PyAudio Installation Issues

Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

### Microphone Not Working

- Check Windows privacy settings
- Ensure microphone permissions are granted
- Test with: `python -m audio_input`

### API Errors

- Verify API keys in `.env`
- Check API quota and billing
- Review logs for detailed error messages

## 📝 Logs

Logs are output to console. To save to file:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    filename='anay.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🔮 Future Enhancements

- Wake word detection
- Multi-user support
- Voice activity detection (VAD)
- Emotion detection in voice
- Plugin system for skills
- Mobile app integration

## 📄 License

Private project.

## 🙏 Acknowledgments

- Deepgram for STT
- Google Gemini for LLM
- ElevenLabs for TTS
- PyAudio, Pygame for audio I/O
