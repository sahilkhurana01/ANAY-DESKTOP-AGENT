import { useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Volume2 } from "lucide-react";

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface TranscriptPanelProps {
  messages: Message[];
  isListening?: boolean;
}

const TranscriptPanel = ({ messages, isListening = false }: TranscriptPanelProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages]);

  return (
    <div className="anay-panel h-full flex flex-col overflow-hidden relative">
      <div className="flex items-center justify-between gap-3 border-b border-white/6 px-4 py-3 flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-3 bg-primary/40 rounded-sm" />
          <h2 className="font-orbitron text-[10px] md:text-xs tracking-widest text-[#9ffcf4] font-bold uppercase">
            Transcript
          </h2>
        </div>
        <div className={`flex items-center gap-2 rounded-full border px-2.5 py-1 text-[10px] font-orbitron uppercase tracking-[0.22em] ${
          isListening ? "border-cyan-300/30 bg-cyan-400/10 text-cyan-100" : "border-white/10 bg-white/[0.03] text-white/45"
        }`}>
          {isListening ? <Volume2 className="w-3 h-3" /> : <Activity className="w-3 h-3" />}
          {isListening ? "Listening" : "Standby"}
        </div>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-4 md:px-5 md:py-5 space-y-6 custom-scrollbar"
      >
        <AnimatePresence mode="popLayout">
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex flex-col ${message.role === "user" ? "items-end" : "items-start"}`}
            >
              <div className="flex items-center gap-2 mb-2 px-1">
                <span className={`text-[10px] font-orbitron font-black tracking-widest ${
                  message.role === "user" ? "text-white/40" : "text-[#9ffcf4]"
                }`}>
                  {message.role === "user" ? "YOU" : "ANAY"}
                </span>
              </div>

              <div
                className={`max-w-[90%] px-4 py-3 rounded-[1.25rem] border text-[14px] leading-relaxed font-rajdhani font-medium ${
                  message.role === "user" ? "anay-transcript-user rounded-tr-md" : "anay-transcript-ai rounded-tl-md"
                }`}
              >
                {message.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-20">
            <div className="anay-orb !h-16 !w-16 !text-base">
              <Activity className="w-5 h-5 text-cyan-200" />
            </div>
            <div className="mt-5 font-orbitron text-sm tracking-[0.35em] uppercase text-white/30">
          TRANSCRIPT
            </div>
            <div className="mt-2 text-white/45 uppercase tracking-[0.24em] text-xs font-orbitron">
              Waiting for input
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TranscriptPanel;
