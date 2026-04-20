import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import type { LucideIcon } from "lucide-react";
import {
  Brain,
  Cpu,
  CreditCard,
  Eye,
  FileText,
  Home,
  Layers,
  Link2,
  MemoryStick,
  Mic,
  MicOff,
  Minimize2,
  PanelLeftClose,
  PanelLeftOpen,
  PanelTopOpen,
  Pin,
  Plus,
  Radio,
  Send,
  Settings,
  Smartphone,
  Square,
  Timer,
  Users,
  Volume2,
  VolumeX,
} from "lucide-react";

import ContactManager from "@/components/ContactManager";
import MemoryViewer from "@/components/MemoryViewer";
import ModelSwitcher from "@/components/ModelSwitcher";
import ModelSwitcherInline from "@/components/ModelSwitcherInline";
import SettingsPanel from "@/components/SettingsPanel";
import TaskLog from "@/components/TaskLog";
import VisionInspectPanel from "@/components/VisionInspectPanel";
import { useAnayChat } from "@/hooks/useAnayChat";
import { useRealtimeVoice } from "@/hooks/useRealtimeVoice";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { ANAYWebSocket } from "@/lib/websocket";

type NavItem = { id: string; label: string; icon: LucideIcon; href?: string };

/* ────────────────────────── sidebar nav data ────────────────────────── */
const NAV_ITEMS: NavItem[] = [
  { id: "home", label: "Home", icon: Home },
  { id: "tasks", label: "Work", icon: Layers },
  { id: "contacts", label: "Contacts", icon: Users },
  { id: "memory", label: "History", icon: Brain },
  { id: "notifications", label: "Activity", icon: Radio },
  { id: "apps", label: "Apps", icon: Smartphone },
  { id: "settings", label: "Settings", icon: Settings },
];

/* ────────────────────────── helper components ────────────────────────── */
function ReasoningBlock({ content }: { content: string }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="reasoning-block" style={{
      margin: "4px 0 8px",
      borderRadius: "8px",
      overflow: "hidden",
      border: "1px solid rgba(255,255,255,0.05)",
      background: "rgba(0,0,0,0.2)",
    }}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          width: "100%",
          padding: "6px 10px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: "rgba(255,255,255,0.03)",
          border: "none",
          cursor: "pointer",
          fontSize: "11px",
          color: "#888",
          letterSpacing: "0.05em",
          textTransform: "uppercase",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <Brain style={{ width: 12, height: 12, opacity: 0.5 }} />
          {isExpanded ? "Collapse reasoning" : "Reasoning"}
        </div>
        <span style={{ opacity: 0.5, fontSize: "14px" }}>{isExpanded ? "−" : "+"}</span>
      </button>
      
      {isExpanded && (
        <div style={{
          padding: "10px",
          fontSize: "12px",
          lineHeight: "1.5",
          color: "#aaa",
          whiteSpace: "pre-wrap",
          background: "rgba(0,0,0,0.1)",
          borderTop: "1px solid rgba(255,255,255,0.02)",
        }}>
          {content}
        </div>
      )}
    </div>
  );
}

function formatUptimeSeconds(totalSeconds: number): string {
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

/* ────────────────────────── component ────────────────────────── */
const Index = () => {
  const { toast } = useToast();
  const { messages, isProcessing, isConnected, sendMessage, clearMessages, stopGeneration } = useAnayChat();
  const [status, setStatus] = useState<"idle" | "listening" | "processing" | "speaking">("idle");
  const [activeNav, setActiveNav] = useState("home");
  const [alwaysOnTop, setAlwaysOnTop] = useState(true);
  const [input, setInput] = useState("");
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [selectedModel, setSelectedModel] = useState(() => localStorage.getItem("anay:model") || "groq/llama-3.3-70b");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const hasLoadedRef = useRef(false);

  /* system metrics */
  const [cpuPercent, setCpuPercent] = useState(0);
  const [ramPercent, setRamPercent] = useState(0);
  const [uptimeLabel, setUptimeLabel] = useState("0m");
  const appStartRef = useRef(Date.now());
  /** Wall-clock sync: Date.now() - uptime_seconds*1000 from backend */
  const osBootMsRef = useRef<number | null>(null);

  const stateRef = useRef({
    audioLevel: 0,
    status: "idle" as "idle" | "listening" | "processing" | "speaking",
  });

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    stateRef.current.status = status;
  }, [status]);

  /* auto-scroll chat */
  useEffect(() => {
    if (scrollRef.current) {
      const behavior = hasLoadedRef.current ? "smooth" : "instant";
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior });
      if (!hasLoadedRef.current && messages.length > 0) {
        hasLoadedRef.current = true;
      }
    }
  }, [messages]);

  /* fetch telemetry — live from WebSocket + REST fallback */
  useEffect(() => {
    let mounted = true;

    /* WebSocket live stream (primary) */
    const ws = ANAYWebSocket.getInstance(import.meta.env.VITE_WS_URL || "ws://127.0.0.1:8000/ws");
    const handleMetrics = (msg: { type: string; data?: any }) => {
      if (!mounted || !msg.data) return;
      const d = msg.data;
      const cpu =
        typeof d.cpu_percent === "number"
          ? d.cpu_percent
          : typeof d.cpu_load === "number"
            ? d.cpu_load
            : undefined;
      const ram =
        typeof d.ram_percent === "number"
          ? d.ram_percent
          : typeof d.ram_usage === "number"
            ? d.ram_usage
            : undefined;
      if (typeof cpu === "number") setCpuPercent(cpu);
      if (typeof ram === "number") setRamPercent(ram);
      if (typeof d.uptime_seconds === "number") {
        osBootMsRef.current = Date.now() - d.uptime_seconds * 1000;
        const sec = Math.max(0, Math.floor((Date.now() - osBootMsRef.current) / 1000));
        setUptimeLabel(formatUptimeSeconds(sec));
      }
    };
    ws.on("system_metrics", handleMetrics);

    /* REST fallback (initial load) */
    api
      .getDesktopState()
      .then((data) => {
        if (!mounted) return;
        setCpuPercent(data.system.cpu_percent ?? 0);
        setRamPercent(data.system.ram_percent ?? 0);
        const up = data.system.uptime_seconds;
        if (typeof up === "number") {
          osBootMsRef.current = Date.now() - up * 1000;
          const sec = Math.max(0, Math.floor((Date.now() - osBootMsRef.current) / 1000));
          setUptimeLabel(formatUptimeSeconds(sec));
        }
      })
      .catch(() => {
        /* backend offline, rely on WS */
      });

    return () => {
      mounted = false;
      ws.off("system_metrics", handleMetrics);
    };
  }, []);

  /* uptime ticker — OS uptime when backend sent uptime_seconds, else SPA session */
  useEffect(() => {
    const tick = () => {
      if (osBootMsRef.current != null) {
        const seconds = Math.max(0, Math.floor((Date.now() - osBootMsRef.current) / 1000));
        setUptimeLabel(formatUptimeSeconds(seconds));
        return;
      }
      const seconds = Math.floor((Date.now() - appStartRef.current) / 1000);
      setUptimeLabel(formatUptimeSeconds(seconds));
    };
    tick();
    const timer = window.setInterval(tick, 15000);
    return () => window.clearInterval(timer);
  }, []);

  /* electron settings */
  useEffect(() => {
    window.anayDesktop
      ?.getSettings?.()
      .then((settings) => {
        if (typeof settings?.alwaysOnTop === "boolean") setAlwaysOnTop(settings.alwaysOnTop);
      })
      .catch(() => undefined);
    
    // Load TTS enable state from backend
    api.getSettings()
      .then(s => setTtsEnabled(s.tts_enabled))
      .catch(console.error);
  }, []);

  /* voice */
  const { isListening, isSpeaking, toggleListening } = useRealtimeVoice({
    stateRef,
    onTranscript: () => setStatus("processing"),
    onAiText: () => setStatus("speaking"),
    onError: (error) => toast({ title: "Voice error", description: error, variant: "destructive" }),
  });

  const handleTextSend = useCallback(async () => {
    const msg = input.trim();
    if (!msg || isProcessing) return;
    setInput("");
    setStatus("processing");
    await sendMessage(msg, selectedModel);
    setStatus("idle");
  }, [input, isProcessing, sendMessage, selectedModel]);

  const handleMicToggle = useCallback(() => {
    toggleListening();
    setStatus((c) => (c === "listening" ? "idle" : "listening"));
  }, [toggleListening]);

  const togglePin = useCallback(async () => {
    const result = await window.anayDesktop?.toggleAlwaysOnTop?.();
    if (typeof result?.alwaysOnTop === "boolean") setAlwaysOnTop(result.alwaysOnTop);
  }, []);

  const handleTtsToggle = useCallback(async () => {
    const next = !ttsEnabled;
    setTtsEnabled(next);
    try {
      await api.updateSettings({ tts_enabled: next });
      toast({ 
        title: next ? "TTS Enabled" : "TTS Disabled", 
        description: next ? "ANAY will now speak responses." : "ANAY will keep quiet to save credits." 
      });
    } catch (err) {
      setTtsEnabled(!next);
      toast({ title: "Failed to update TTS", variant: "destructive" });
    }
  }, [ttsEnabled, toast]);

  const hideWindow = useCallback(async () => {
    await window.anayDesktop?.hideWindow?.();
  }, []);

  const minimizeWindow = useCallback(async () => {
    await window.anayDesktop?.minimizeWindow?.();
  }, []);

  const maximizeWindow = useCallback(async () => {
    await window.anayDesktop?.maximizeWindow?.();
  }, []);

  const handleNewChat = useCallback(() => {
    clearMessages();
    toast({ title: "New Chat Started", description: "All previous history cleared." });
  }, [clearMessages, toast]);

  const sessionStatus = isProcessing ? "processing" : isSpeaking ? "speaking" : status;

  const statusLabel =
    sessionStatus === "listening"
      ? "LISTENING"
      : sessionStatus === "processing"
        ? "PROCESSING"
        : sessionStatus === "speaking"
          ? "SPEAKING"
          : "STANDBY";

  /* ───────────── RENDER ───────────── */
  return (
    <div className="anay-shell">
      {/* ──── TITLEBAR ──── */}
      <header className="anay-titlebar">
        <div className="traffic-lights">
          <button
            className="traffic-dot traffic-dot--close"
            onClick={hideWindow}
            aria-label="Close"
          />
          <button 
            className="traffic-dot traffic-dot--minimize" 
            onClick={minimizeWindow}
            aria-label="Minimize" 
          />
          <button 
            className="traffic-dot traffic-dot--maximize" 
            onClick={maximizeWindow}
            aria-label="Maximize" 
          />
        </div>
        <span className="anay-titlebar-brand">ANAY</span>

        {/* Right side controls */}
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8, WebkitAppRegion: "no-drag" } as React.CSSProperties}>
          <button
            onClick={togglePin}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              color: alwaysOnTop ? "#e53935" : "#555",
              display: "flex",
              alignItems: "center",
            }}
            title={alwaysOnTop ? "Pinned" : "Unpinned"}
          >
            <Pin style={{ width: 14, height: 14 }} />
          </button>
          <button
            onClick={hideWindow}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "#555",
              display: "flex",
              alignItems: "center",
            }}
            title="Hide"
          >
            <PanelTopOpen style={{ width: 14, height: 14 }} />
          </button>
        </div>
      </header>

      {/* ──── BODY: sidebar + main ──── */}
      <div className={`anay-body ${isSidebarCollapsed ? "anay-body--collapsed" : ""}`}>
        {/* ──── LEFT SIDEBAR ──── */}
        <aside className="anay-sidebar">
          <div className="sidebar-header" style={{ padding: "0 10px 10px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <button
              onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
              className="sidebar-toggle-btn"
              title={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {isSidebarCollapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
            </button>
            {!isSidebarCollapsed && (
              <button
                onClick={handleNewChat}
                className="new-chat-btn"
                title="New Chat"
              >
                <Plus size={16} />
                <span>New Chat</span>
              </button>
            )}
          </div>

          <div className="sidebar-metrics">
            <MetricCard icon={<Cpu style={{ width: 12, height: 12 }} />} label="CPU" value={`${Math.round(cpuPercent)}%`} percent={cpuPercent} />
            <MetricCard icon={<MemoryStick style={{ width: 12, height: 12 }} />} label="RAM" value={`${Math.round(ramPercent)}%`} percent={ramPercent} />
            <MetricCard icon={<Timer style={{ width: 12, height: 12 }} />} label="Up" value={uptimeLabel} percent={null} />
          </div>

          <div className="sidebar-nav-container main-nav">
            {NAV_ITEMS.filter(i => !["apps", "settings"].includes(i.id)).map((item) => {
              const Icon = item.icon;
              const active = activeNav === item.id;
              const className = `sidebar-nav-item${active ? " sidebar-nav-item--active" : ""}`;
              return (
                <button key={item.id} type="button" className={className} onClick={() => setActiveNav(item.id)}>
                  <Icon />
                  <span className="nav-label">{item.label}</span>
                </button>
              );
            })}
          </div>

          <div className="sidebar-footer">
            <div className="sidebar-nav-container footer-nav">
              {NAV_ITEMS.filter(i => ["apps", "settings"].includes(i.id)).map((item) => {
                const Icon = item.icon;
                const active = activeNav === item.id;
                const className = `sidebar-nav-item${active ? " sidebar-nav-item--active" : ""}`;
                return (
                  <button key={item.id} type="button" className={className} onClick={() => setActiveNav(item.id)}>
                    <Icon />
                    <span className="nav-label">{item.label}</span>
                  </button>
                );
              })}
            </div>

            {/* connection status */}
            <div className="connection-status-container">
              <div
                className="connection-status"
                style={{ color: isConnected ? "#e53935" : "#333" }}
              >
                <div
                  className="status-dot"
                  style={{ background: isConnected ? "#e53935" : "#333" }}
                />
                {!isSidebarCollapsed && (
                  <span className="status-text">
                    {isConnected ? "Backend linked" : "Backend offline"}
                  </span>
                )}
              </div>
            </div>
            
            {!isSidebarCollapsed && <div className="sidebar-version">v2.0.0</div>}
          </div>
        </aside>

        {/* ──── CENTER MAIN ──── */}
        {activeNav === "home" ? (
          <main className="anay-main">

            {/* ── Orb zone ── */}
            <div className={`orb-zone orb-zone--${sessionStatus}`}>
              <div className="anay-orb-container">
                <div className="anay-orb-ring anay-orb-ring--outer" />
                <div className="anay-orb-ring anay-orb-ring--inner" />
                <div className="anay-orb-sphere" />
              </div>
              <div className="orb-status">
                <span className="orb-status-dot" />
                {statusLabel}
              </div>
            </div>

            {/* ── Chat area ── */}
            <div className="chat-area" style={{ flex: messages.length > 0 ? "0 0 auto" : undefined, maxHeight: "45%" }}>
              {messages.length > 0 ? (
                <div ref={scrollRef} className="chat-messages" style={{ maxHeight: 240, overflowY: "auto" }}>
                  {messages.map((msg) => (
                    <div key={msg.id} className={`msg-row msg-row--${msg.role === "user" ? "user" : "ai"}`}>
                      {msg.role === "assistant" ? (
                        <div className="anay-mini-orb" />
                      ) : (
                        <div className="msg-avatar msg-avatar--user">Boss</div>
                      )}
                      <div className={`msg-bubble msg-bubble--${msg.role === "user" ? "user" : "ai"}`}>
                        {msg.role === "assistant" && msg.reasoning && (
                          <ReasoningBlock content={msg.reasoning} />
                        )}
                        <div className="msg-content">{msg.content}</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-chat">Awaiting input</div>
              )}

              {/* Input bar */}
              <div className="chat-input-bar">
                <div style={{ marginRight: "10px", display: "flex", alignItems: "center" }}>
                  <ModelSwitcherInline 
                    selected={selectedModel} 
                    onChange={(id) => {
                      setSelectedModel(id);
                      localStorage.setItem("anay:model", id);
                    }} 
                  />
                </div>
                <button
                  type="button"
                  onClick={handleMicToggle}
                  disabled={isProcessing}
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 6,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    border: "1px solid",
                    borderColor: isListening ? "#e53935" : "#1e1e1e",
                    background: isListening ? "rgba(229,57,53,0.15)" : "#0f0f0f",
                    cursor: "pointer",
                    flexShrink: 0,
                    color: isListening ? "#e53935" : "#555",
                  }}
                  title={isListening ? "Stop listening" : "Start listening"}
                >
                  {isListening ? <MicOff style={{ width: 14, height: 14 }} /> : <Mic style={{ width: 14, height: 14 }} />}
                </button>

                <input
                  className="chat-input"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleTextSend();
                    }
                  }}
                  placeholder="Message ANAY..."
                  disabled={isProcessing || isListening}
                />

                <button
                  type="button"
                  className={`chat-send-btn ${isProcessing ? "chat-stop-btn" : ""}`}
                  onClick={isProcessing ? stopGeneration : handleTextSend}
                  disabled={!isProcessing && !input.trim()}
                  title={isProcessing ? "Stop" : "Send"}
                  style={isProcessing ? { background: "rgba(229,57,53,0.1)", color: "#e53935", border: "1px solid #e5393533" } : {}}
                >
                  {isProcessing ? <Square style={{ width: 14, height: 14, fill: "currentColor" }} /> : <Send />}
                </button>

                <button
                  type="button"
                  onClick={clearMessages}
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 6,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    border: "1px solid #1e1e1e",
                    background: "#0f0f0f",
                    cursor: "pointer",
                    flexShrink: 0,
                    color: "#555",
                    marginLeft: 4
                  }}
                  title="Clear Chat"
                >
                  <Timer style={{ width: 14, height: 14 }} />
                </button>

                <button
                  type="button"
                  onClick={handleTtsToggle}
                  disabled={isProcessing}
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 6,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    border: "1px solid",
                    borderColor: ttsEnabled ? "#22c55e33" : "#1e1e1e",
                    background: ttsEnabled ? "rgba(34,197,94,0.05)" : "#0f0f0f",
                    cursor: "pointer",
                    flexShrink: 0,
                    color: ttsEnabled ? "#22c55e" : "#555",
                    marginLeft: 4
                  }}
                  title={ttsEnabled ? "TTS On" : "TTS Off"}
                >
                  {ttsEnabled ? <Volume2 style={{ width: 14, height: 14 }} /> : <VolumeX style={{ width: 14, height: 14 }} />}
                </button>
              </div>
            </div>
          </main>
        ) : (
          <main className="anay-main" style={{ overflowY: "auto", padding: "12px 16px 20px" }}>
            <div style={{ maxWidth: 720, margin: "0 auto", width: "100%", display: "flex", flexDirection: "column", gap: 16 }}>
              {activeNav === "tasks" && <TaskLog />}
              {activeNav === "contacts" && <ContactManager />}
              {activeNav === "memory" && <MemoryViewer />}
              {activeNav === "settings" && <SettingsPanel />}
              {(activeNav === "notifications" || activeNav === "apps") && (
                <div style={{ padding: 40, textAlign: "center", opacity: 0.5 }}>
                  <Radio style={{ width: 48, height: 48, marginBottom: 12, opacity: 0.2 }} />
                  <p>Monitoring system events...</p>
                </div>
              )}
            </div>
          </main>
        )}
      </div>
    </div>
  );
};

/* ─── MetricCard ─── */
const MetricCard = ({
  icon,
  label,
  value,
  percent,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  percent: number | null;
}) => (
  <div className="metric-card">
    <div className="metric-card-header">
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        {icon}
        <span className="metric-card-label">{label}</span>
      </div>
      <span className="metric-card-value">{value}</span>
    </div>
    {percent !== null && (
      <div className="metric-bar">
        <div className="metric-bar-fill" style={{ width: `${Math.min(percent, 100)}%` }} />
      </div>
    )}
  </div>
);

export default Index;
