import { useEffect, useState } from "react";
import { BellRing, Pin, Radio, Volume2, VolumeX } from "lucide-react";

import { api } from "@/lib/api";

const SettingsPanel = () => {
  const [launchOnStartup, setLaunchOnStartup] = useState(false);
  const [voiceMode, setVoiceMode] = useState("push_to_talk");
  const [ttsEnabled, setTtsEnabled] = useState(false);

  useEffect(() => {
    api.getSettings().then((settings) => {
      setVoiceMode(settings.voice_mode);
      setTtsEnabled(settings.tts_enabled);
    }).catch(console.error);
    window.anayDesktop?.getSettings?.().then((settings) => {
      setLaunchOnStartup(Boolean(settings.launchOnStartup));
    }).catch(() => undefined);
  }, []);

  const toggleStartup = async () => {
    const result = await window.anayDesktop?.toggleLaunchOnStartup?.();
    if (typeof result?.launchOnStartup === "boolean") {
      setLaunchOnStartup(result.launchOnStartup);
    }
  };

  const changeVoiceMode = async (nextMode: string) => {
    setVoiceMode(nextMode);
    await api.updateSettings({ voice_mode: nextMode });
  };

  const toggleTts = async () => {
    const next = !ttsEnabled;
    setTtsEnabled(next);
    await api.updateSettings({ tts_enabled: next });
  };

  return (
    <div className="anay-panel p-5 flex flex-col gap-4">
      <div>
        <p className="font-orbitron text-xs tracking-[0.35em] text-primary uppercase">Permissions</p>
        <h3 className="text-2xl font-orbitron font-black text-white">Desktop Settings</h3>
      </div>

      <button onClick={toggleStartup} className="rounded-[1.35rem] border border-white/10 bg-white/[0.03] p-4 text-left hover:bg-white/[0.05]">
        <div className="flex items-center gap-3">
          <BellRing className="w-4 h-4 text-cyan-300" />
          <div>
            <div className="text-white font-semibold">Launch on Startup</div>
            <div className="text-sm text-white/50">
              {launchOnStartup ? "Enabled for login startup" : "Disabled until you turn it on"}
            </div>
          </div>
        </div>
      </button>

      <div className="rounded-[1.35rem] border border-white/10 bg-white/[0.03] p-4 space-y-3">
        <div className="flex items-center gap-3">
          <Radio className="w-4 h-4 text-cyan-300" />
          <div className="text-white font-semibold">Voice Mode</div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {[
            { value: "push_to_talk", label: "Push to Talk" },
            { value: "always_on", label: "Always Listening" },
          ].map((option) => (
            <button
              key={option.value}
              onClick={() => changeVoiceMode(option.value)}
              className={`rounded-2xl border px-3 py-3 text-sm ${
                voiceMode === option.value
                  ? "border-cyan-300/50 bg-cyan-400/[0.08] text-white"
                  : "border-white/10 bg-black/20 text-white/65"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <button onClick={toggleTts} className="rounded-[1.35rem] border border-white/10 bg-white/[0.03] p-4 text-left hover:bg-white/[0.05]">
        <div className="flex items-center gap-3">
          {ttsEnabled ? <Volume2 className="w-4 h-4 text-cyan-300" /> : <VolumeX className="w-4 h-4 text-red-400" />}
          <div>
            <div className="text-white font-semibold">Voice Responses (TTS)</div>
            <div className="text-sm text-white/50">
              {ttsEnabled ? "ANAY will speak responses (Sarvam AI)" : "Muted (Saves API Credits)"}
            </div>
          </div>
        </div>
      </button>

      <div className="rounded-[1.35rem] border border-white/10 bg-white/[0.03] p-4 text-sm text-white/60">
        <div className="flex items-center gap-2 mb-2 text-white">
          <Pin className="w-4 h-4 text-cyan-300" />
          Native controls
        </div>
        Use `Ctrl + Space` to summon ANAY instantly from anywhere after Electron is running.
      </div>
    </div>
  );
};

export default SettingsPanel;
