import { useState } from "react";

const MODELS = [
  { id: "groq/llama-3.3-70b",        label: "Groq Versatile",   tag: "Smart",   color: "#10b981" },
  { id: "groq/llama-3.1-8b",         label: "Groq Instant",     tag: "Fastest", color: "#3b82f6" },
  { id: "openrouter/glm-4.5",        label: "GLM 4.5 Air",      tag: "Cool",    color: "#8b5cf6" },
  { id: "openrouter/minimax-2.5",    label: "MiniMax 2.5",      tag: "Pro",     color: "#f59e0b" },
  { id: "openrouter/gpt-oss",        label: "GPT-OSS 120B",     tag: "Heavy",   color: "#06b6d4" },
  { id: "openrouter/nemotron-super",  label: "Nemotron 120B",    tag: "Smart",   color: "#8b5cf6" },
  { id: "openrouter/deepseek-r1",     label: "DeepSeek R1",      tag: "Reason",  color: "#f59e0b" },
  { id: "openrouter/nemotron-nano",   label: "Nemotron Nano",    tag: "Light",   color: "#ec4899" },
  { id: "openrouter/gemma3",          label: "Gemma 3 27B",      tag: "Free",    color: "#06b6d4" },
  { id: "gemini/flash",               label: "Gemini Flash",     tag: "Vision",  color: "#ec4899" },
];

interface ModelSwitcherProps {
  selected: string;
  onChange: (id: string) => void;
}

export default function ModelSwitcherInline({ selected, onChange }: ModelSwitcherProps) {
  const [open, setOpen] = useState(false);
  const current = MODELS.find(m => m.id === selected) || MODELS[0];

  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      {/* Trigger button — shows in chat input bar */}
      <button
        onClick={() => setOpen(!open)}
        style={{
          display: "flex", alignItems: "center", gap: "6px",
          padding: "4px 10px", borderRadius: "20px",
          border: "1px solid #333", background: "#1a1a1a",
          color: "#fff", fontSize: "12px", cursor: "pointer",
          whiteSpace: "nowrap"
        }}
      >
        <span style={{
          width: 8, height: 8, borderRadius: "50%",
          background: current.color, display: "inline-block"
        }} />
        {current.label}
        <span style={{ opacity: 0.5 }}>▾</span>
      </button>

      {/* Dropdown */}
      {open && (
        <div style={{
          position: "absolute", bottom: "36px", left: 0,
          background: "#111", border: "1px solid #333",
          borderRadius: "12px", padding: "8px",
          minWidth: "220px", zIndex: 100,
          boxShadow: "0 8px 32px rgba(0,0,0,0.5)"
        }}>
          <div style={{ fontSize: "10px", color: "#666",
            padding: "4px 8px 8px", textTransform: "uppercase",
            letterSpacing: "0.08em" }}>
            Select Model
          </div>
          {MODELS.map(m => (
            <div
              key={m.id}
              onClick={() => { onChange(m.id); setOpen(false) }}
              style={{
                display: "flex", alignItems: "center",
                justifyContent: "space-between",
                padding: "8px 10px", borderRadius: "8px",
                cursor: "pointer",
                background: selected === m.id ? "#1e1e2e" : "transparent",
                marginBottom: "2px",
              }}
              onMouseEnter={e => e.currentTarget.style.background = "#1e1e2e"}
              onMouseLeave={e => e.currentTarget.style.background =
                selected === m.id ? "#1e1e2e" : "transparent"}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{
                  width: 8, height: 8, borderRadius: "50%",
                  background: m.color, flexShrink: 0
                }} />
                <span style={{ fontSize: "13px", color: "#e0e0e0" }}>
                  {m.label}
                </span>
              </div>
              <span style={{
                fontSize: "10px", padding: "2px 6px",
                borderRadius: "4px", background: "#222",
                color: "#888"
              }}>
                {m.tag}
              </span>
            </div>
          ))}
          <div style={{
            fontSize: "10px", color: "#444",
            padding: "8px 8px 2px", borderTop: "1px solid #222",
            marginTop: "4px"
          }}>
            All free • Auto-fallback enabled
          </div>
        </div>
      )}
    </div>
  );
}
