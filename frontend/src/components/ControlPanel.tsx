import { motion } from 'framer-motion';
import { Mic, MicOff, Video, VideoOff, Power } from 'lucide-react';

interface ControlPanelProps {
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

const ControlPanel = ({
  isListening,
  isSpeaking,
  isVideoOn,
  onMicToggle,
  onVideoToggle,
  onEnd,
  onStart,
  isSessionActive,
  status,
}: ControlPanelProps) => {
  const getStatusText = () => {
    switch (status) {
      case 'listening':
        return 'LISTENING';
      case 'processing':
        return 'PROCESSING';
      case 'speaking':
        return 'SPEAKING';
      default:
        return 'READY';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'listening':
        return 'text-anay-green';
      case 'processing':
        return 'text-accent';
      case 'speaking':
        return 'text-primary';
      default:
        return 'text-muted-foreground';
    }
  };

  return (
    <div className="flex flex-col items-center">
      {/* Control Capsule */}
      <div className="bg-[#111] border border-white/5 rounded-full px-2 py-1.5 flex items-center gap-4 shadow-2xl">
        {/* Video Button - Left */}
        <button
          onClick={onVideoToggle}
          className="p-2 rounded-full hover:bg-white/5 transition-colors group"
        >
          {isVideoOn ? (
            <Video className="w-4 h-4 text-foreground/40 group-hover:text-foreground" />
          ) : (
            <VideoOff className="w-4 h-4 text-foreground/40 group-hover:text-foreground" />
          )}
        </button>

        {/* START/END Toggle Button - Center */}
        <motion.button
          onClick={isSessionActive ? onEnd : onStart}
          className={`${isSessionActive ? 'bg-[#601a1a] hover:bg-[#802a2a] border-[#ff4d4d]/20' : 'bg-[#1a6020] hover:bg-[#2a8030] border-[#4dff4d]/20'} border px-6 py-2 rounded-full flex items-center gap-2 group transition-all`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Power className="w-3.5 h-3.5 text-white" />
          <span className="font-orbitron font-black text-xs text-white tracking-widest">
            {isSessionActive ? 'END' : 'START'}
          </span>
        </motion.button>

        {/* Mic Button - Right */}
        <button
          onClick={onMicToggle}
          className="p-2 rounded-full hover:bg-white/5 transition-colors group"
        >
          {isListening ? (
            <Mic className="w-4 h-4 text-foreground/40 group-hover:text-foreground" />
          ) : (
            <MicOff className="w-4 h-4 text-foreground/40 group-hover:text-foreground" />
          )}
        </button>
      </div>
    </div>
  );
};

export default ControlPanel;
