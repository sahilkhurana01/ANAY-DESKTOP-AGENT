import { useState, useCallback, useEffect, useRef } from 'react';
import { ANAYWebSocket, ServerMessage } from '@/lib/websocket';

interface UseRealtimeVoiceProps {
    onTranscript?: (text: string, isFinal: boolean) => void;
    onAiText?: (text: string) => void;
    onError?: (error: string) => void;
    stateRef: React.MutableRefObject<{
        audioLevel: number;
        status: 'idle' | 'listening' | 'processing' | 'speaking';
    }>;
}

export const useRealtimeVoice = ({
    onTranscript,
    onAiText,
    onError,
    stateRef
}: UseRealtimeVoiceProps) => {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [isConnected, setIsConnected] = useState(false);

    const wsRef = useRef<ANAYWebSocket | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioAnalyserRef = useRef<AnalyserNode | null>(null);
    const animationFrameRef = useRef<number | null>(null);

    // Audio playback queue - store Audio objects for MP3 playback
    const audioQueueRef = useRef<HTMLAudioElement[]>([]);
    const isPlayingRef = useRef(false);
    /** Set synchronously so level metering works before React re-renders `isListening`. */
    const listeningActiveRef = useRef(false);

    // Initialize WebSocket
    useEffect(() => {
        const wsUrl = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws';
        const ws = ANAYWebSocket.getInstance(wsUrl);
        wsRef.current = ws;

        const onOpen = () => {
            setIsConnected(true);
            console.log('WebSocket connected to backend');
        };

        // Check initial connection state
        if (ws.isConnected()) {
            onOpen();
        }

        const onClose = () => setIsConnected(false);

        const onPartialTranscript = (data: ServerMessage) => {
            if (data.type === 'partial_transcript') onTranscript?.(data.payload, false);
        };

        const onFinalTranscript = (data: ServerMessage) => {
            if (data.type === 'final_transcript') onTranscript?.(data.payload, true);
        };

        const onResponse = (data: ServerMessage) => {
            if (data.type === 'response') {
                onAiText?.(data.content);
            }
        };

        const onAiTextEvent = (data: ServerMessage) => {
            if (data.type === 'ai_text') {
                stateRef.current.status = 'speaking';
                onAiText?.(data.payload);
            }
        };

        const onAudioLevel = (data: ServerMessage) => {
            if (data.type === 'audio_level') {
                stateRef.current.audioLevel = data.payload;
            }
        };

        const onTtsAudio = (data: ServerMessage) => {
            if (data.type === 'tts_audio') {
                handleIncomingAudio(data.payload);
            }
        };

        const onAudioChunk = (data: ServerMessage) => {
            if (data.type === 'audio_chunk' && 'audio' in data) {
                handleIncomingAudio(data.audio);
            }
        };

        ws.on('open', onOpen);
        ws.on('close', onClose);
        ws.on('partial_transcript', onPartialTranscript);
        ws.on('final_transcript', onFinalTranscript);
        ws.on('response', onResponse);
        ws.on('ai_text', onAiTextEvent);
        ws.on('audio_level', onAudioLevel);
        ws.on('tts_audio', onTtsAudio);
        ws.on('audio_chunk', onAudioChunk);

        ws.connect().catch(err => onError?.(err.message));

        return () => {
            ws.off('open', onOpen);
            ws.off('close', onClose);
            ws.off('partial_transcript', onPartialTranscript);
            ws.off('final_transcript', onFinalTranscript);
            ws.off('response', onResponse);
            ws.off('ai_text', onAiTextEvent);
            ws.off('audio_level', onAudioLevel);
            ws.off('tts_audio', onTtsAudio);
            ws.off('audio_chunk', onAudioChunk);
            stopListening();
        };
    }, []);

    const handleIncomingAudio = (base64Audio: string) => {
        try {
            const binary = atob(base64Audio);
            const len = binary.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) bytes[i] = binary.charCodeAt(i);

            // Eleven Labs sends MP3, not PCM - decode as MP3
            if (!audioContextRef.current) {
                audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
            }

            // Create blob and decode MP3
            const blob = new Blob([bytes], { type: 'audio/mpeg' });
            const audioUrl = URL.createObjectURL(blob);

            const audio = new Audio(audioUrl);
            audio.onended = () => {
                URL.revokeObjectURL(audioUrl);
                setIsSpeaking(false);
                stateRef.current.status = 'idle';
                if (audioQueueRef.current.length > 0) {
                    playNextInQueue();
                } else {
                    isPlayingRef.current = false;
                }
            };

            audio.onerror = (e) => {
                console.error('Audio playback error:', e);
                URL.revokeObjectURL(audioUrl);
                setIsSpeaking(false);
                isPlayingRef.current = false;
            };

            if (!isPlayingRef.current) {
                isPlayingRef.current = true;
                setIsSpeaking(true);
                stateRef.current.status = 'speaking';
                audio.play().catch(err => {
                    console.error('Failed to play audio:', err);
                    isPlayingRef.current = false;
                    setIsSpeaking(false);
                });
            } else {
                // Queue audio if already playing
                audioQueueRef.current.push(audio);
            }
        } catch (error) {
            console.error('Error handling incoming audio:', error);
        }
    };

    const playNextInQueue = () => {
        if (audioQueueRef.current.length === 0) {
            isPlayingRef.current = false;
            setIsSpeaking(false);
            stateRef.current.status = 'idle';
            stateRef.current.audioLevel = 0;
            return;
        }

        isPlayingRef.current = true;
        setIsSpeaking(true);
        stateRef.current.status = 'speaking';

        const audio = audioQueueRef.current.shift()!;

        audio.onended = () => {
            playNextInQueue();
        };

        audio.onerror = () => {
            console.error('Audio playback error');
            playNextInQueue();
        };

        audio.play().catch(err => {
            console.error('Failed to play queued audio:', err);
            playNextInQueue();
        });
    };

    // Update audio level visualization
    const updateAudioLevel = () => {
        if (!audioAnalyserRef.current || !listeningActiveRef.current) {
            stateRef.current.audioLevel = 0;
            return;
        }

        const dataArray = new Uint8Array(audioAnalyserRef.current.frequencyBinCount);
        audioAnalyserRef.current.getByteFrequencyData(dataArray);

        // Calculate average volume
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        stateRef.current.audioLevel = average / 255; // Normalize to 0-1

        animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    };

    const startListening = async () => {
        try {
            listeningActiveRef.current = true;
            console.log('[MediaRecorder] Starting audio capture...');

            // Create audio context if needed
            if (!audioContextRef.current) {
                audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
            }

            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000
                }
            });
            streamRef.current = stream;
            console.log('[MediaRecorder] Got microphone stream');

            // Create analyser for visual  feedback
            const source = audioContextRef.current.createMediaStreamSource(stream);
            const analyser = audioContextRef.current.createAnalyser();
            analyser.fftSize = 256;
            source.connect(analyser);
            audioAnalyserRef.current = analyser;

            // Start visual feedback loop
            updateAudioLevel();

            // Create MediaRecorder
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                ? 'audio/webm;codecs=opus'
                : 'audio/webm';

            const mediaRecorder = new MediaRecorder(stream, {
                mimeType,
                audioBitsPerSecond: 16000
            });
            mediaRecorderRef.current = mediaRecorder;

            mediaRecorder.ondataavailable = async (event) => {
                if (event.data.size > 0 && wsRef.current) {
                    console.log('[MediaRecorder] Audio chunk captured, size:', event.data.size);

                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64 = (reader.result as string).split(',')[1];
                        console.log('[MediaRecorder] Sending final audio blob to WebSocket');
                        wsRef.current?.send({ type: 'audio_chunk', payload: base64 } as any);
                        
                        // If we are stopping, ensure stop_audio is sent AFTER the data
                        if (mediaRecorder.state === 'inactive') {
                            console.log('[MediaRecorder] Final blob sent, triggering backend process');
                            wsRef.current?.send({ type: 'stop_audio' } as any);
                        }
                    };
                    reader.readAsDataURL(event.data);
                }
            };

            mediaRecorder.onerror = (error) => {
                console.error('[MediaRecorder] Error:', error);
                onError?.('Audio recording error');
            };

            // Start recording - no timeslice for best reliability
            mediaRecorder.start();
            console.log('[MediaRecorder] Recording started');

            setIsListening(true);
            stateRef.current.status = 'listening';
        } catch (err) {
            listeningActiveRef.current = false;
            console.error('[MediaRecorder] Error starting:', err);
            onError?.(err instanceof Error ? err.message : String(err));
        }
    };

    const stopListening = () => {
        console.log('[MediaRecorder] Stopping audio capture...');
        listeningActiveRef.current = false;

        setIsListening(false);
        stateRef.current.status = 'idle';
        stateRef.current.audioLevel = 0;

        // Stop animation frame
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
            animationFrameRef.current = null;
        }

        // Stop media recorder
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current = null;
        }

        // Stop media stream
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }

        audioAnalyserRef.current = null;
    };

    const toggleListening = () => {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    };

    return {
        isListening,
        isSpeaking,
        isConnected,
        toggleListening,
        startListening,
        stopListening
    };
};
