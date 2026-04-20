import { useState, useEffect, useCallback, useRef } from 'react';

interface UseSpeechRecognitionProps {
  onResult: (transcript: string) => void;
  onAudioLevel?: (level: number) => void;
  language?: string;
}

export const useSpeechRecognition = ({
  onResult,
  onAudioLevel,
  language = 'hi-IN'
}: UseSpeechRecognitionProps) => {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef<any>(null);
  const isListeningRef = useRef(false);
  const lastHeardAtRef = useRef<number>(0);
  const langCycleRef = useRef<string[]>(['hi-IN', 'en-IN', 'en-US', 'pa-IN']);
  const langIndexRef = useRef<number>(0);
  const autoSwitchTimerRef = useRef<number | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      setIsSupported(true);
      // Create once; don't recreate on isListening changes (stale closures can break restart).
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = language;

      recognition.onresult = (event: any) => {
        lastHeardAtRef.current = Date.now();
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          onResult(finalTranscript);
        }
      };

      recognition.onerror = (event: any) => {
        // Handle different error types
        if (event.error === 'no-speech') {
          // No speech detected - this is normal, keep listening
          return;
        } else if (event.error === 'network') {
          // Network errors are often false positives from the browser's speech API
          // The API works offline but still reports "network" errors
          // Only log in development, don't stop listening
          if (import.meta.env.DEV) {
            console.debug('Speech recognition network event (ignoring):', event.error);
          }
          return;
        } else if (event.error === 'audio-capture') {
          // Microphone not available
          console.error('Microphone not available');
          isListeningRef.current = false;
          setIsListening(false);
        } else if (event.error === 'not-allowed') {
          // Permission denied
          console.error('Microphone permission denied');
          isListeningRef.current = false;
          setIsListening(false);
        } else if (event.error === 'aborted') {
          // Recognition was aborted - don't stop, just restart
          return;
        } else {
          // Other errors - log but don't stop listening
          console.warn('Speech recognition error (continuing):', event.error);
        }
      };

      recognition.onend = () => {
        // Some browsers auto-stop; restart if user still wants listening.
        if (isListeningRef.current) {
          try {
            recognition.start();
          } catch (e) {
            // InvalidStateError if already started; ignore.
          }
        }
      };

      recognitionRef.current = recognition;
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch {
          // ignore
        }
      }
      if (autoSwitchTimerRef.current) {
        window.clearInterval(autoSwitchTimerRef.current);
        autoSwitchTimerRef.current = null;
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [language, onResult]);

  // Keep recognition language in sync if the prop changes.
  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = language;
    }
  }, [language]);

  const startAudioAnalysis = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStreamRef.current = stream;

      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;

      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);

      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const updateLevel = () => {
        if (analyserRef.current && onAudioLevel) {
          analyserRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
          const normalizedLevel = average / 255;
          onAudioLevel(normalizedLevel);
        }
        animationFrameRef.current = requestAnimationFrame(updateLevel);
      };

      updateLevel();
    } catch (error) {
      console.error('Error accessing microphone for audio analysis:', error);
    }
  }, [onAudioLevel]);

  const stopAudioAnalysis = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach(track => track.stop());
      micStreamRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    if (onAudioLevel) {
      onAudioLevel(0);
    }
  }, [onAudioLevel]);

  const startListening = useCallback(async () => {
    if (!recognitionRef.current) {
      console.error('Speech recognition not initialized');
      return;
    }

    // Check if already listening
    if (isListeningRef.current) {
      console.log('Already listening, skipping start');
      return;
    }

    try {
      console.log('Starting speech recognition...');
      isListeningRef.current = true;
      setIsListening(true);

      // Ensure mic permission prompt happens (also drives audio level).
      await startAudioAnalysis();

      // Start with requested language, but auto-switch if nothing is heard.
      recognitionRef.current.lang = language;
      langIndexRef.current = Math.max(0, langCycleRef.current.indexOf(language));
      lastHeardAtRef.current = Date.now();

      try {
        recognitionRef.current.start();
      } catch {
        // ignore InvalidStateError
      }

      // Auto-switch language if user speaks but recognition returns nothing.
      if (!autoSwitchTimerRef.current) {
        autoSwitchTimerRef.current = window.setInterval(() => {
          if (!isListeningRef.current || !recognitionRef.current) return;
          const silenceMs = Date.now() - lastHeardAtRef.current;
          if (silenceMs < 8000) return;

          // Rotate to next language
          langIndexRef.current = (langIndexRef.current + 1) % langCycleRef.current.length;
          const nextLang = langCycleRef.current[langIndexRef.current];
          console.log('Auto-switching STT language to', nextLang);
          try {
            recognitionRef.current.stop();
          } catch { }
          recognitionRef.current.lang = nextLang;
          lastHeardAtRef.current = Date.now();
          try {
            recognitionRef.current.start();
          } catch { }
        }, 1500);
      }
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      isListeningRef.current = false;
      setIsListening(false);
    }
  }, [startAudioAnalysis]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      isListeningRef.current = false;
      try {
        recognitionRef.current.stop();
      } catch {
        // ignore
      }
      if (autoSwitchTimerRef.current) {
        window.clearInterval(autoSwitchTimerRef.current);
        autoSwitchTimerRef.current = null;
      }
      setIsListening(false);
      stopAudioAnalysis();
    }
  }, [stopAudioAnalysis]);

  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  return {
    isListening,
    isSupported,
    startListening,
    stopListening,
    toggleListening,
  };
};
