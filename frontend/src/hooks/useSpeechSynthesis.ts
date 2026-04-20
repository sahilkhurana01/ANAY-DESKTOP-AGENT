import { useState, useCallback, useEffect, useRef } from 'react';

interface UseSpeechSynthesisProps {
  onStart?: () => void;
  onEnd?: () => void;
  onAudioLevel?: (level: number) => void;
  language?: string;
}

export const useSpeechSynthesis = ({
  onStart,
  onEnd,
  onAudioLevel,
  language = 'hi-IN',
}: UseSpeechSynthesisProps) => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    setIsSupported('speechSynthesis' in window);
  }, []);

  const simulateAudioLevel = useCallback((text: string = '') => {
    if (!isSpeaking || !onAudioLevel) return;

    // Create a more realistic audio pattern based on text
    const words = text.split(/\s+/);
    let wordIndex = 0;
    const startTime = Date.now();
    const avgWordDuration = 300; // ms per word

    const updateLevel = () => {
      if (!isSpeaking) {
        onAudioLevel(0);
        return;
      }

      const elapsed = Date.now() - startTime;
      const currentWordIndex = Math.floor(elapsed / avgWordDuration);
      
      // Simulate speech pattern: higher levels during words, lower during pauses
      const wordProgress = (elapsed % avgWordDuration) / avgWordDuration;
      
      // Create wave pattern: peak in middle of word, lower at edges
      let level = 0.2;
      if (wordProgress < 0.9) {
        // During word: create sine wave pattern
        const wave = Math.sin(wordProgress * Math.PI * 2);
        level = 0.3 + Math.abs(wave) * 0.5;
        
        // Add some randomness for natural variation
        level += (Math.random() - 0.5) * 0.15;
        level = Math.max(0.2, Math.min(0.9, level));
      } else {
        // Pause between words: lower level
        level = 0.15 + Math.random() * 0.1;
      }

      // Add emphasis variation (some words louder)
      if (currentWordIndex % 3 === 0) {
        level *= 1.2;
        level = Math.min(0.95, level);
      }

      onAudioLevel(level);
      animationRef.current = requestAnimationFrame(updateLevel);
    };

    updateLevel();
  }, [isSpeaking, onAudioLevel]);

  const speak = useCallback((text: string) => {
    if (!isSupported) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;
    utterance.rate = 0.9;
    utterance.pitch = 1;

    // Try to find a Hindi voice
    const voices = window.speechSynthesis.getVoices();
    const hindiVoice = voices.find(voice => 
      voice.lang.includes('hi') || voice.lang.includes('Hindi')
    );
    
    if (hindiVoice) {
      utterance.voice = hindiVoice;
    }

    utterance.onstart = () => {
      setIsSpeaking(true);
      onStart?.();
      if (onAudioLevel) {
        simulateAudioLevel(text);
      }
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      onEnd?.();
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      onAudioLevel?.(0);
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setIsSpeaking(false);
      onEnd?.();
      onAudioLevel?.(0);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [isSupported, language, onStart, onEnd, onAudioLevel, simulateAudioLevel]);

  const cancel = useCallback(() => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    onAudioLevel?.(0);
    onEnd?.();
  }, [onEnd, onAudioLevel]);

  // Load voices
  useEffect(() => {
    const loadVoices = () => {
      window.speechSynthesis.getVoices();
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return {
    isSpeaking,
    isSupported,
    speak,
    cancel,
  };
};
