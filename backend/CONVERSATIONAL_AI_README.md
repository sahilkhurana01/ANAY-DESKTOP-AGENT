# Conversational AI Assistant

This module implements a complete conversational AI pipeline following the exact hierarchy from the flowchart:

## Pipeline Flow

1. **PyAudio Library** → Captures physical audio input from microphone
2. **Recording .wav file** → Saves audio to WAV file
3. **Deepgram API** → Converts audio to text (transcript string)
4. **OpenAI API** → Generates AI response (response string)
5. **Eleven Labs API** → Converts text to speech (speech .wav file)
6. **Pygame Library** → Plays audio output physically

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit `api.txt` in the project root and add your API keys:

```
Deepgram = your_deepgram_api_key
Eleven Labs = your_elevenlabs_api_key
OpenAI = your_openai_api_key
```

**Note:** You need to replace `YOUR_OPENAI_API_KEY_HERE` in `api.txt` with your actual OpenAI API key.

### 3. Run the Assistant

```bash
cd backend
python conversational_ai.py
```

## Features

- **Continuous Conversation**: The assistant runs in a loop, continuously listening and responding
- **High-Quality Voice**: Uses Eleven Labs with optimized voice settings for natural speech
- **Smart AI Responses**: Uses OpenAI GPT-4o-mini for intelligent, contextual responses
- **Automatic Transcription**: Deepgram API handles speech-to-text conversion
- **Talkback Function**: Full bidirectional conversation capability

## Usage

1. Run `python conversational_ai.py`
2. The assistant will start recording audio (default: 5 seconds)
3. Speak your question or message
4. Wait for the AI to process and respond
5. The response will be played through your speakers
6. The cycle repeats automatically

## Configuration

You can customize the assistant in `conversational_ai.py`:

```python
assistant = ConversationalAI(
    record_duration=5.0,  # How long to record (seconds)
    sample_rate=16000,     # Audio sample rate
    language="en"          # Language: "en" for English, "hi" for Hindi
)
```

## Voice Settings

The assistant uses optimized Eleven Labs voice settings:
- **Stability**: 0.5 (balanced)
- **Similarity Boost**: 0.75 (high quality)
- **Speaker Boost**: Enabled (enhanced clarity)
- **Voice**: Rachel (professional, clear female voice)

## Troubleshooting

### No audio input detected
- Check your microphone permissions
- Ensure microphone is connected and working
- Try adjusting `record_duration` if you speak slowly

### API errors
- Verify all API keys are correct in `api.txt`
- Check your API quotas/limits
- Ensure you have internet connection

### Audio playback issues
- Check your speakers/headphones
- Ensure Pygame is properly installed
- Try adjusting system volume

## Exit

Press `Ctrl+C` to stop the assistant gracefully.
