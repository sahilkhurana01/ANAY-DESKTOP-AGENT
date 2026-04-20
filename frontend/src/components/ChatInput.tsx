import { useState, KeyboardEvent } from "react";
import { motion } from "framer-motion";
import { Keyboard, Send, Mic, MicOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface ChatInputProps {
  onSend: (message: string) => Promise<void>;
  isProcessing?: boolean;
  isListening?: boolean;
  onMicToggle?: () => void;
  onVoiceInput?: (text: string) => void;
}

const ChatInput = ({ onSend, isProcessing = false, isListening = false, onMicToggle, onVoiceInput }: ChatInputProps) => {
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return;

    const message = input.trim();
    setInput('');
    await onSend(message);
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.2 }} className="anay-panel p-3 sm:p-4 flex-shrink-0">
      <div className="flex items-center gap-2 sm:gap-3">
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Button
            onClick={onMicToggle}
            disabled={isProcessing}
            variant={isListening ? "destructive" : "secondary"}
            className={`rounded-2xl px-4 py-3 ${isListening ? 'bg-red-500 hover:bg-red-600' : ''}`}
          >
            {isListening ? (
              <MicOff className="w-4 h-4 sm:w-5 sm:h-5" />
            ) : (
              <Mic className="w-4 h-4 sm:w-5 sm:h-5" />
            )}
          </Button>
        </motion.div>
        <div className="flex-1 relative">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="w-full h-14 font-rajdhani rounded-[1.2rem] px-4 sm:px-5 py-3 sm:py-3.5 bg-black/25 border-white/10 focus:border-primary/40 focus:ring-2 focus:ring-primary/15 transition-all duration-300 placeholder:text-white/28"
            disabled={isProcessing || isListening}
          />
          <div className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 hidden md:flex items-center gap-2 text-[10px] uppercase tracking-[0.24em] text-white/25 font-orbitron">
            <Keyboard className="w-3 h-3" />
            Enter
          </div>
        </div>
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isProcessing}
            className="anay-button-primary px-4 sm:px-6 py-3 sm:py-3.5 rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4 sm:w-5 sm:h-5 mr-1 sm:mr-2" />
            <span className="hidden sm:inline">Send</span>
          </Button>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default ChatInput;
