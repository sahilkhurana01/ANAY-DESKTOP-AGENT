import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import ParticleOrb from './ParticleOrb';
import ControlPanel from './ControlPanel';

interface CoreSystemProps {
  stateRef: React.MutableRefObject<{
    audioLevel: number;
    status: 'idle' | 'listening' | 'processing' | 'speaking';
  }>;
  frequency?: string;
  // Control props for integration
  isListening: boolean;
  isSpeaking: boolean;
  isVideoOn: boolean;
  onMicToggle: () => void;
  onVideoToggle: () => void;
  onEnd: () => void;
  onStart: () => void;
  isSessionActive: boolean;
  status: 'idle' | 'listening' | 'processing' | 'speaking';
}

const CoreSystem = ({
  stateRef,
  frequency: propFrequency,
  isListening,
  isSpeaking,
  isVideoOn,
  onMicToggle,
  onVideoToggle,
  onEnd,
  onStart,
  isSessionActive,
  status
}: CoreSystemProps) => {
  const [frequency, setFrequency] = useState('0-0kHz');

  useEffect(() => {
    let animationId: number;
    let audioContext: AudioContext | null = null;
    let analyser: AnalyserNode | null = null;
    let microphone: MediaStreamAudioSourceNode | null = null;

    const startFrequencyAnalysis = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new AudioContext();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;
        microphone = audioContext.createMediaStreamSource(stream);
        microphone.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        const updateFrequency = () => {
          if (!analyser) return;

          analyser.getByteFrequencyData(dataArray);

          // Find dominant frequency range
          let maxAmplitude = 0;
          let dominantIndex = 0;

          for (let i = 0; i < dataArray.length; i++) {
            if (dataArray[i] > maxAmplitude) {
              maxAmplitude = dataArray[i];
              dominantIndex = i;
            }
          }

          // Calculate frequency from index
          const nyquist = audioContext!.sampleRate / 2;
          const dominantFreq = (dominantIndex * nyquist) / analyser.frequencyBinCount;

          // Format frequency range
          const freqKHz = dominantFreq / 1000;
          const rangeStart = Math.max(0, Math.floor(freqKHz - 0.5));
          const rangeEnd = Math.ceil(freqKHz + 0.5);

          setFrequency(`${rangeStart}-${rangeEnd}kHz`);

          animationId = requestAnimationFrame(updateFrequency);
        };

        updateFrequency();
      } catch (err) {
        console.error('Microphone access denied for frequency analysis:', err);
        setFrequency('0-0kHz');
      }
    };

    if (isListening || isSpeaking) {
      startFrequencyAnalysis();
    } else {
      setFrequency('0-0kHz');
    }

    return () => {
      if (animationId) cancelAnimationFrame(animationId);
      if (microphone) microphone.disconnect();
      if (audioContext) audioContext.close();
    };
  }, [isListening, isSpeaking]);

  return (
    <div className="h-full w-full flex flex-col bg-[#050505] border-[#1a1a1a] rounded-xl overflow-hidden relative">
      {/* Header */}
      <div className="p-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-primary opacity-80">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <h2 className="font-orbitron text-[10px] md:text-xs tracking-[0.2em] text-[#00f5d4] font-bold uppercase">
            CORE SYSTEM
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[9px] text-foreground/30 font-orbitron font-bold tracking-widest uppercase">FREQ:</span>
          <span className="text-[10px] text-foreground/50 font-orbitron font-bold tracking-widest">{propFrequency || frequency}</span>
        </div>
      </div>

      {/* Particle Orb Container */}
      <div className="flex-1 relative overflow-hidden flex items-center justify-center">
        <ParticleOrb stateRef={stateRef} />

        {/* Subtle grid overlay - removed to match flat image but kept a very light version */}
        <div
          className="absolute inset-0 pointer-events-none opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(hsl(180 100% 50% / 0.1) 1px, transparent 1px),
              linear-gradient(90deg, hsl(180 100% 50% / 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '80px 80px',
          }}
        />

        {/* Floating Controls Overlay */}
        <div className="absolute bottom-6 left-0 right-0 z-20">
          <ControlPanel
            isListening={isListening}
            isSpeaking={isSpeaking}
            isVideoOn={isVideoOn}
            onMicToggle={onMicToggle}
            onVideoToggle={onVideoToggle}
            onEnd={onEnd}
            onStart={onStart}
            isSessionActive={isSessionActive}
            status={status}
          />
        </div>
      </div>
    </div>
  );
};

export default CoreSystem;
