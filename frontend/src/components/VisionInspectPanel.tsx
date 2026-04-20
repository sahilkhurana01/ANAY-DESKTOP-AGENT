import { useState } from "react";
import { Eye, Loader2 } from "lucide-react";

import { api } from "@/lib/api";

const VisionInspectPanel = () => {
  const [prompt, setPrompt] = useState("What is on screen? Summarize briefly.");
  const [analysis, setAnalysis] = useState("");
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    const p = prompt.trim() || "Describe the desktop.";
    setLoading(true);
    setError("");
    try {
      const res = await api.inspectScreen(p);
      setAnalysis(res.analysis || "");
      setPreview(res.screenshot_base64 ? `data:image/png;base64,${res.screenshot_base64}` : null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Vision request failed.");
      setAnalysis("");
      setPreview(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="anay-panel p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-orbitron text-xs tracking-[0.35em] text-primary uppercase">Desktop</p>
          <h3 className="text-2xl font-orbitron font-black text-white">Vision</h3>
        </div>
        <Eye className="w-5 h-5 text-cyan-300" />
      </div>

      <p className="text-sm text-white/55">
        Captures the screen and sends it to your configured vision model. Ensure Gemini or another vision backend is set up in the backend.
      </p>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        className="w-full min-h-[88px] rounded-[1.35rem] border border-white/10 bg-black/20 p-3 text-white placeholder:text-white/35 outline-none resize-y"
        placeholder="Ask what to look for..."
      />

      <button
        type="button"
        onClick={run}
        disabled={loading}
        className="anay-button-primary px-4 py-2 text-sm inline-flex items-center justify-center gap-2 disabled:opacity-50"
      >
        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
        {loading ? "Inspecting…" : "Capture & analyze"}
      </button>

      {error ? <p className="text-sm text-red-400">{error}</p> : null}

      {preview ? (
        <div className="rounded-[1rem] border border-white/10 overflow-hidden bg-black/40">
          <img src={preview} alt="Last capture" className="w-full max-h-[280px] object-contain" />
        </div>
      ) : null}

      {analysis ? (
        <div className="rounded-[1.35rem] border border-white/10 bg-white/[0.03] p-4 text-sm text-white/85 whitespace-pre-wrap">
          {analysis}
        </div>
      ) : null}
    </div>
  );
};

export default VisionInspectPanel;
