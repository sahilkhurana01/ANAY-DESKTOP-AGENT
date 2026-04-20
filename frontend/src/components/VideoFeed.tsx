import { useRef, useEffect, useState } from 'react';
import { VideoOff } from 'lucide-react';

interface VideoFeedProps {
  isVideoOn: boolean;
  onToggle: () => void;
}

const VideoFeed = ({ isVideoOn }: VideoFeedProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isVideoOn) {
      navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((mediaStream) => {
          setStream(mediaStream);
          if (videoRef.current) {
            videoRef.current.srcObject = mediaStream;
          }
          setError(null);
        })
        .catch((err) => {
          console.error('Error accessing camera:', err);
          setError('Camera not available');
        });
    } else {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
        setStream(null);
      }
    }

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [isVideoOn]);

  return (
    <div className="anay-panel h-full flex flex-col bg-[#050505] border-[#1a1a1a]">
      {/* Header */}
      <div className="p-3 flex items-center gap-2 flex-shrink-0">
        <VideoOff className="w-3.5 h-3.5 text-primary opacity-80" />
        <h2 className="font-orbitron text-[10px] md:text-xs tracking-widest text-[#00f5d4] font-bold">
          VISUAL INPUT
        </h2>
      </div>

      {/* Video Container */}
      <div className="flex-1 relative flex items-center justify-center overflow-hidden">
        {isVideoOn ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className="w-full h-full object-cover opacity-80"
            />
            <div className="absolute top-2 left-2 flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-primary/10 border border-primary/30">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              <span className="text-[8px] text-primary font-orbitron">CAM_ACTIVE</span>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center gap-4 text-foreground/40">
            <VideoOff className="w-12 h-12 stroke-[1.5]" />
            <span className="text-[10px] font-orbitron tracking-widest uppercase">
              VIDEO FEED OFFLINE
            </span>
          </div>
        )}

        {error && (
          <div className="absolute bottom-2 left-2 right-2 bg-destructive/10 border border-destructive/30 rounded px-2 py-1">
            <span className="text-[9px] text-destructive uppercase tracking-tighter">{error}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoFeed;
