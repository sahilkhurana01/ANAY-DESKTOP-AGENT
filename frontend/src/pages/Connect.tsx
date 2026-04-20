import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Link as LinkIcon, Globe, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAnayChat } from '@/hooks/useAnayChat';

const Connect = () => {
  const { isConnected } = useAnayChat();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Trigger reconnection
    window.location.reload();
  };

  const connectionStatus = isConnected ? 'CONNECTED' : 'DISCONNECTED';
  const statusColor = isConnected ? 'text-anay-green' : 'text-destructive';

  return (
    <div className="h-full flex flex-col gap-4 p-4">
      <Link to="/" className="text-xs font-orbitron text-muted-foreground hover:text-primary w-fit">
        ← Back to ANAY
      </Link>
      <div className="anay-panel p-6 flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center gap-2">
          <LinkIcon className="w-6 h-6 text-primary" />
          <h2 className="font-orbitron text-primary text-xl tracking-wider anay-glow-text">
            CONNECT
          </h2>
        </div>

        {/* Connection Status */}
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg">
            <div className="flex items-center gap-3">
              {isConnected ? (
                <Wifi className="w-6 h-6 text-anay-green" />
              ) : (
                <WifiOff className="w-6 h-6 text-destructive" />
              )}
              <div>
                <p className="font-orbitron text-sm text-muted-foreground">BACKEND STATUS</p>
                <p className={`font-orbitron text-lg ${statusColor}`}>{connectionStatus}</p>
              </div>
            </div>
            <Button
              onClick={handleRefresh}
              disabled={isRefreshing}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>

          {/* Connection Info */}
          <div className="space-y-3">
            <div className="p-4 bg-secondary/30 rounded-lg">
              <p className="text-xs text-muted-foreground font-orbitron mb-2">CONNECTION DETAILS</p>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">WebSocket URL:</span>
                  <span className="text-foreground font-mono text-xs">
                    {import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">API URL:</span>
                  <span className="text-foreground font-mono text-xs">
                    {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <span className={statusColor}>
                    {isConnected ? '● ONLINE' : '● OFFLINE'}
                  </span>
                </div>
              </div>
            </div>

            {/* Instructions */}
            {!isConnected && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-4 bg-destructive/10 border border-destructive/30 rounded-lg"
              >
                <p className="text-sm text-destructive font-orbitron mb-2">CONNECTION FAILED</p>
                <p className="text-xs text-muted-foreground">
                  Make sure the backend server is running:
                </p>
                <code className="block mt-2 p-2 bg-background rounded text-xs">
                  cd backend && python main.py
                </code>
              </motion.div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="pt-4 border-t border-border/30">
            <p className="text-xs text-muted-foreground font-orbitron mb-3">QUICK ACTIONS</p>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant="outline"
                className="justify-start"
                onClick={() => window.open('https://anay-backend.onrender.com/', '_blank')}
              >
                <Globe className="w-4 h-4 mr-2" />
                Health Check
              </Button>
              <Button
                variant="outline"
                className="justify-start"
                onClick={() => window.open('https://anay-backend.onrender.com/docs', '_blank')}
              >
                <LinkIcon className="w-4 h-4 mr-2" />
                API Docs
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Connect;
