import { useEffect, useState } from "react";
import { Bot, MonitorUp, WifiOff } from "lucide-react";

import { api } from "@/lib/api";

const MODEL_OPTIONS = [
  { value: "auto", label: "Auto Route", hint: "Groq short tasks, MiniMax deep tasks" },
  { value: "groq/llama-3.3-70b", label: "Groq Versatile", hint: "Llama 3.3 70B - Smart & Fast" },
  { value: "groq/llama-3.1-8b", label: "Groq Instant", hint: "Ultra-fast response (8B)" },
  { value: "minimax", label: "MiniMax M2.7", hint: "Heavy reasoning via NVIDIA NIM" },
  { value: "gemini", label: "Gemini", hint: "Fallback and vision-heavy work" },
  { value: "ollama", label: "Ollama", hint: "Offline local inference" },
];

const ModelSwitcher = () => {
  const [model, setModel] = useState("auto");
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    api
      .getSettings()
      .then((settings) => {
        setModel(settings.default_model);
        setOffline(settings.offline_mode);
        localStorage.setItem("anay:model", settings.default_model);
        localStorage.setItem("anay:offline", settings.offline_mode ? "true" : "false");
      })
      .catch(() => {
        const m = localStorage.getItem("anay:model") || "auto";
        const o = localStorage.getItem("anay:offline") === "true";
        setModel(m);
        setOffline(o);
      });
  }, []);

  const updateModel = async (nextModel: string) => {
    setModel(nextModel);
    localStorage.setItem("anay:model", nextModel);
    await api.updateSettings({ default_model: nextModel });
  };

  const toggleOffline = async () => {
    const next = !offline;
    setOffline(next);
    localStorage.setItem("anay:offline", next ? "true" : "false");
    await api.updateSettings({ offline_mode: next });
  };

  return (
    <div className="anay-panel p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-orbitron text-xs tracking-[0.35em] text-primary uppercase">Routing</p>
          <h3 className="text-2xl font-orbitron font-black text-white">Model Switcher</h3>
        </div>
        <Bot className="w-5 h-5 text-cyan-300" />
      </div>

      <div className="grid gap-2">
        {MODEL_OPTIONS.map((option) => (
          <button
            key={option.value}
            onClick={() => updateModel(option.value)}
            className={`rounded-[1.35rem] border p-3.5 text-left transition-all ${
              model === option.value
                ? "border-cyan-300/40 bg-cyan-400/[0.08] shadow-[0_0_0_1px_rgba(103,232,249,0.08)]"
                : "border-white/10 bg-white/[0.03] hover:bg-white/[0.05]"
            }`}
          >
            <div className="flex items-center justify-between gap-3">
              <span className="text-white font-semibold">{option.label}</span>
              {model === option.value && <MonitorUp className="w-4 h-4 text-cyan-300" />}
            </div>
            <div className="text-sm text-white/50">{option.hint}</div>
          </button>
        ))}
      </div>

      <button
        onClick={toggleOffline}
        className={`rounded-[1.35rem] border px-4 py-3 text-left ${
          offline ? "border-emerald-400/30 bg-emerald-500/10" : "border-white/10 bg-white/[0.03] hover:bg-white/[0.05]"
        }`}
      >
        <div className="flex items-center gap-3">
          <WifiOff className="w-4 h-4 text-emerald-300" />
          <div>
            <div className="text-white font-semibold">Offline Preference</div>
            <div className="text-sm text-white/50">
              {offline ? "Prefer Ollama/local execution" : "Cloud routing allowed"}
            </div>
          </div>
        </div>
      </button>
    </div>
  );
};

export default ModelSwitcher;
