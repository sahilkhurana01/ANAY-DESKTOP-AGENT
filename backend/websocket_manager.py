from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import tempfile
import time
from typing import Dict, List, Optional

from fastapi import WebSocket, WebSocketDisconnect
from dotenv import load_dotenv

from audio_converter import convert_webm_to_wav
from llm_router import llm_router
from speech_to_text import SpeechToText
from system_monitor import system_monitor
from settings import runtime_settings
from tts.edge_tts_streamer import EdgeTTSStreamer
from tts.sarvam_stream import SarvamStreamer

load_dotenv()

logger = logging.getLogger(__name__)


def _benign_websocket_close(exc: BaseException) -> bool:
    """Normal client/server shutdowns — not application bugs."""
    if isinstance(exc, WebSocketDisconnect):
        return True
    s = repr(exc)
    for token in ("1006", "1012", "1001", "1000", "1011"):
        if token in s:
            return True
    return False


def calculate_amplitude(base64_audio: str) -> float:
    try:
        audio_bytes = base64.b64decode(base64_audio)
        if len(audio_bytes) < 10:
            return 0.0
            
        # If it's WebM (starts with \x1a\x45\xdf\xa3), we can't easily calculate RMS without decoding
        # Return a "heartbeat" value to show the system is receiving audio packets
        if audio_bytes.startswith(b"\x1a\x45\xdf\xa3"):
            import random
            return 0.3 + (random.random() * 0.2) # Pulsing between 0.3 and 0.5
            
        samples = [
            int.from_bytes(audio_bytes[i:i + 2], "little", signed=True)
            for i in range(0, min(len(audio_bytes), 1000), 2)
        ]
        if not samples: return 0.0
        rms = (sum(sample * sample for sample in samples) / len(samples)) ** 0.5
        return min(1.0, rms / 32768.0 * 10)
    except Exception:
        return 0.1


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.audio_buffer: Dict[str, List[bytes]] = {}
        self.session_headers: Dict[str, bytes] = {}
        self.buffer_start_time: Dict[str, float] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await websocket.send_json({"type": "status", "status": "idle"})

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        ws_id = str(id(websocket))
        self.audio_buffer.pop(ws_id, None)
        self.session_headers.pop(ws_id, None)
        self.buffer_start_time.pop(ws_id, None)

    async def broadcast_metrics(self):
        while True:
            if self.active_connections:
                payload = {"type": "system_metrics", "data": system_monitor.get_metrics_payload()}
                for websocket in list(self.active_connections):
                    try:
                        await websocket.send_json(payload)
                    except Exception:
                        self.disconnect(websocket)
            await asyncio.sleep(3)

    async def broadcast_notification(self, message: str):
        payload = {
            "type": "response",
            "content": f"Reminder: {message}",
            "role": "assistant",
            "timestamp": time.time(),
        }
        for websocket in list(self.active_connections):
            try:
                await websocket.send_json(payload)
            except Exception:
                self.disconnect(websocket)

    async def broadcast_chat_event(self, role: str, content: str, meta: dict = None):
        """Broadcast a message to all connected clients (used for Telegram sync)."""
        payload = {
            "type": "user_message" if role == "user" else "response",
            "content": content,
            "message": content,
            "text": content,
            "role": role,
            "timestamp": time.time(),
            "meta": meta or {}
        }
        for websocket in list(self.active_connections):
            try:
                await websocket.send_json(payload)
            except Exception:
                self.disconnect(websocket)

    async def _speak(self, websocket: WebSocket, text: str):
        """Skip synthesis if disabled in settings."""
        if not runtime_settings.tts_enabled:
            logger.info("TTS is disabled; skipping voice synthesis.")
            return

        """Try Sarvam AI first; on failure use Edge TTS."""
        sarvam_key = os.getenv("SARVAM_API_KEY")
        streamers: List[tuple[str, object]] = []
        if sarvam_key and len(sarvam_key) > 10:
            try:
                streamers.append(("Sarvam AI", SarvamStreamer(sarvam_key, speaker="kabir")))
            except Exception as exc:
                logger.warning("Sarvam AI init failed: %s", exc)
        
        # Always fallback to Edge TTS with a delay-retry aware wrapper if possible
        streamers.append(("Edge TTS", EdgeTTSStreamer()))

        last_error: Optional[Exception] = None
        for label, streamer in streamers:
            audio_chunks: List[bytes] = []
            try:
                async for audio_chunk in streamer.stream_text(text):
                    if not audio_chunk:
                        continue
                    audio_chunks.append(audio_chunk)
                    level = calculate_amplitude(base64.b64encode(audio_chunk).decode("utf-8"))
                    await websocket.send_json({"type": "audio_level", "payload": level})
                if audio_chunks:
                    audio_base64 = base64.b64encode(b"".join(audio_chunks)).decode("utf-8")
                    await websocket.send_json(
                        {"type": "tts_audio", "payload": audio_base64, "audio": audio_base64}
                    )
                    if label != "Sarvam AI":
                        logger.info("Voice reply used %s (Sarvam AI unavailable or empty).", label)
                    return
                logger.warning("%s returned no audio; trying next engine.", label)
            except Exception as exc:
                last_error = exc
                logger.warning("%s failed (%s); trying next TTS engine.", label, exc)

        if last_error:
            logger.error("All TTS engines failed: %s", last_error)

    async def _send_router_response(self, websocket: WebSocket, user_message: str):
        await websocket.send_json({"type": "status", "status": "processing"})
        try:
            response = await asyncio.to_thread(
                llm_router.chat,
                prompt=user_message,
                preferred_model=runtime_settings.default_model,
                offline=runtime_settings.offline_mode,
            )
        except Exception as exc:
            logger.error("Chat router failed in voice session: %s", exc)
            text = "Model ne error throw kar di — thodi der baad dubara bol, ya chhota sentence try kar."
            await websocket.send_json(
                {
                    "type": "response",
                    "content": text,
                    "message": text,
                    "text": text,
                    "timestamp": time.time(),
                    "role": "assistant",
                    "meta": {"provider": "error", "model": "none", "tool_calls": [], "error": str(exc)},
                }
            )
            await websocket.send_json({"type": "status", "status": "speaking"})
            await self._speak(websocket, text)
            await websocket.send_json({"type": "status", "status": "idle"})
            return

        text = response["text"]
        await websocket.send_json(
            {
                "type": "response",
                "content": text,
                "message": text,
                "text": text,
                "timestamp": time.time(),
                "role": "assistant",
                "meta": {
                    "provider": response["provider"],
                    "model": response["model"],
                    "tool_calls": response["tool_calls"],
                },
            }
        )
        await websocket.send_json({"type": "status", "status": "speaking"})
        await self._speak(websocket, text)
        await websocket.send_json({"type": "status", "status": "idle"})

    async def _process_audio_buffer(self, websocket: WebSocket, ws_id: str):
        if ws_id not in self.audio_buffer or not self.audio_buffer[ws_id]:
            return

        chunks = self.audio_buffer[ws_id]
        if chunks and not chunks[0].startswith(b"\x1a\x45\xdf\xa3") and ws_id in self.session_headers:
            combined_audio = self.session_headers[ws_id] + b"".join(chunks)
        else:
            combined_audio = b"".join(chunks)
            
        logger.info(f"[AI] Processing final audio accumulation ({len(combined_audio)} bytes)...")

        self.audio_buffer[ws_id] = []
        temp_audio = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
        temp_wav_path: Optional[str] = None
        try:
            temp_audio.write(combined_audio)
            temp_audio.close()
            temp_wav_path = await asyncio.to_thread(convert_webm_to_wav, temp_audio.name)
            transcript = await asyncio.to_thread(
                SpeechToText().transcribe, temp_wav_path, "hi"
            )
            transcript = transcript.strip()
            if not transcript:
                await websocket.send_json({"type": "status", "status": "idle"})
                return
            await websocket.send_json({"type": "final_transcript", "payload": transcript})
            await websocket.send_json(
                {
                    "type": "user_message",
                    "content": transcript,
                    "message": transcript,
                    "text": transcript,
                    "timestamp": time.time(),
                    "role": "user",
                }
            )
            await self._send_router_response(websocket, transcript)
        except ValueError as exc:
            logger.error("Voice STT not configured: %s", exc)
            err_text = (
                "Voice needs Deepgram: set DEEPGRAM_API_KEY in backend/.env "
                "or add `Deepgram=...` to api.txt, then restart the backend."
            )
            await websocket.send_json(
                {
                    "type": "response",
                    "content": err_text,
                    "message": err_text,
                    "text": err_text,
                    "timestamp": time.time(),
                    "role": "assistant",
                    "meta": {"provider": "voice", "model": "none", "tool_calls": [], "error": str(exc)},
                }
            )
            await websocket.send_json({"type": "status", "status": "idle"})
        except Exception as exc:
            logger.exception("Voice transcription failed")
            err_text = f"Mic audio decode ya transcription fail: {exc}"
            await websocket.send_json(
                {
                    "type": "response",
                    "content": err_text,
                    "message": err_text,
                    "text": err_text,
                    "timestamp": time.time(),
                    "role": "assistant",
                    "meta": {"provider": "voice", "model": "none", "tool_calls": [], "error": str(exc)},
                }
            )
            await websocket.send_json({"type": "status", "status": "idle"})
        finally:
            try:
                os.unlink(temp_audio.name)
            except Exception:
                pass
            if temp_wav_path:
                try:
                    os.unlink(temp_wav_path)
                except Exception:
                    pass

    async def handle_voice_session(self, websocket: WebSocket):
        try:
            while True:
                raw = await websocket.receive_text()
                message = json.loads(raw)
                msg_type = message.get("type")
                payload = message.get("payload")
                content = message.get("content")
                ws_id = str(id(websocket))

                if msg_type == "request_metrics":
                    await websocket.send_json({"type": "system_metrics", "data": system_monitor.get_metrics_payload()})
                    continue

                if msg_type in {"message", "text_input"}:
                    user_message = payload or content
                    if not user_message:
                        continue
                    await websocket.send_json(
                        {
                            "type": "user_message",
                            "content": user_message,
                            "message": user_message,
                            "text": user_message,
                            "timestamp": time.time(),
                            "role": "user",
                        }
                    )
                    await self._send_router_response(websocket, user_message)
                    continue

                if msg_type == "audio_chunk":
                    audio_bytes = base64.b64decode(payload)
                    if ws_id not in self.audio_buffer:
                        self.audio_buffer[ws_id] = []
                        self.buffer_start_time[ws_id] = time.time()
                        await websocket.send_json({"type": "status", "status": "listening"})

                    if ws_id not in self.session_headers and audio_bytes.startswith(b"\x1a\x45\xdf\xa3"):
                        self.session_headers[ws_id] = audio_bytes
                    self.audio_buffer[ws_id].append(audio_bytes)
                    await websocket.send_json({"type": "audio_level", "payload": calculate_amplitude(payload)})
                    continue

                if msg_type == "stop_audio":
                    await self._process_audio_buffer(websocket, ws_id)
                    continue
        except WebSocketDisconnect:
            logger.debug("WebSocket disconnected (client left).")
        except Exception as exc:
            if _benign_websocket_close(exc):
                logger.debug("WebSocket closed: %s", exc)
            else:
                logger.error("WebSocket session error: %s", exc)
        finally:
            self.disconnect(websocket)
