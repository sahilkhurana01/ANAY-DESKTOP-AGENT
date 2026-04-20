import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Phone, PhoneCall, PhoneOff, History, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface CallHistory {
  id: string;
  number: string;
  name?: string;
  type: 'incoming' | 'outgoing' | 'missed';
  duration?: number;
  timestamp: Date;
}

const Phone = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isCalling, setIsCalling] = useState(false);
  const [callHistory, setCallHistory] = useState<CallHistory[]>([]);

  // Load call history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('anay_call_history');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setCallHistory(parsed.map((c: any) => ({
          ...c,
          timestamp: new Date(c.timestamp),
        })));
      } catch (e) {
        console.error('Error loading call history:', e);
      }
    }
  }, []);

  const handleCall = () => {
    if (phoneNumber.trim()) {
      setIsCalling(true);
      // Simulate call
      setTimeout(() => {
        const call: CallHistory = {
          id: Date.now().toString(),
          number: phoneNumber,
          type: 'outgoing',
          duration: Math.floor(Math.random() * 300),
          timestamp: new Date(),
        };
        setCallHistory([call, ...callHistory]);
        localStorage.setItem('anay_call_history', JSON.stringify([call, ...callHistory]));
        setIsCalling(false);
        setPhoneNumber('');
      }, 2000);
    }
  };

  const handleEndCall = () => {
    setIsCalling(false);
    setPhoneNumber('');
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="h-full flex flex-col gap-4 p-4">
      <Link to="/" className="text-xs font-orbitron text-muted-foreground hover:text-primary w-fit">
        ← Back to ANAY
      </Link>
      <div className="anay-panel p-6 flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center gap-2">
          <Phone className="w-6 h-6 text-primary" />
          <h2 className="font-orbitron text-primary text-xl tracking-wider anay-glow-text">
            PHONE
          </h2>
        </div>

        {/* Dialer */}
        <div className="space-y-4">
          <div className="p-4 bg-secondary/30 rounded-lg">
            <Input
              placeholder="Enter phone number"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ''))}
              className="text-2xl text-center font-orbitron"
              disabled={isCalling}
            />
          </div>

          {/* Number Pad */}
          <div className="grid grid-cols-3 gap-2">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, '*', 0, '#'].map((num) => (
              <Button
                key={num}
                onClick={() => !isCalling && setPhoneNumber(prev => prev + num)}
                className="h-16 text-xl font-orbitron"
                variant="outline"
                disabled={isCalling}
              >
                {num}
              </Button>
            ))}
          </div>

          {/* Call Buttons */}
          <div className="flex gap-2">
            {isCalling ? (
              <Button
                onClick={handleEndCall}
                className="flex-1 bg-destructive hover:bg-destructive/90"
                size="lg"
              >
                <PhoneOff className="w-5 h-5 mr-2" />
                End Call
              </Button>
            ) : (
              <Button
                onClick={handleCall}
                disabled={!phoneNumber.trim()}
                className="flex-1"
                size="lg"
              >
                <PhoneCall className="w-5 h-5 mr-2" />
                Call
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Call History */}
      <div className="flex-1 anay-panel overflow-hidden flex flex-col">
        <div className="p-4 border-b border-border/30 flex items-center gap-2">
          <History className="w-4 h-4 text-primary" />
          <span className="text-xs text-muted-foreground font-orbitron">CALL HISTORY</span>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {callHistory.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <Phone className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No call history</p>
            </div>
          ) : (
            callHistory.map((call, index) => (
              <motion.div
                key={call.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg hover:bg-secondary/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${
                    call.type === 'incoming' ? 'bg-anay-green/20' :
                    call.type === 'missed' ? 'bg-destructive/20' :
                    'bg-primary/20'
                  }`}>
                    {call.type === 'incoming' ? (
                      <PhoneCall className="w-4 h-4 text-anay-green" />
                    ) : call.type === 'missed' ? (
                      <PhoneOff className="w-4 h-4 text-destructive" />
                    ) : (
                      <PhoneCall className="w-4 h-4 text-primary" />
                    )}
                  </div>
                  <div>
                    <p className="font-orbitron text-foreground">{call.number}</p>
                    <p className="text-xs text-muted-foreground">
                      {call.timestamp.toLocaleDateString()} {call.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">{formatDuration(call.duration)}</p>
                  <p className="text-xs text-muted-foreground capitalize">{call.type}</p>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Phone;
