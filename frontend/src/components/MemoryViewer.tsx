import { useEffect, useState } from "react";
import { Brain, Trash2 } from "lucide-react";

import { MemoryItem, api } from "@/lib/api";

const MemoryViewer = () => {
  const [items, setItems] = useState<MemoryItem[]>([]);
  const [draft, setDraft] = useState("");

  const load = async () => {
    try {
      const data = await api.getMemory();
      setItems(data.items);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const remember = async () => {
    if (!draft.trim()) return;
    await api.remember(draft.trim(), "preference");
    setDraft("");
    load();
  };

  return (
    <div className="anay-panel h-full p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-orbitron text-xs tracking-[0.35em] text-primary uppercase">Persistent Memory</p>
          <h3 className="text-2xl font-orbitron font-black text-white">What ANAY Knows</h3>
        </div>
        <Brain className="w-5 h-5 text-cyan-300" />
      </div>

      <div className="rounded-[1.35rem] border border-white/10 bg-black/20 p-3 space-y-3">
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder='Try: "Remember that I prefer Brave over Chrome."'
          className="w-full h-20 bg-transparent outline-none text-white placeholder:text-white/35 resize-none"
        />
        <button onClick={remember} className="anay-button-primary px-4 py-2 text-sm">
          Remember This
        </button>
      </div>

      <div className="flex-1 overflow-auto custom-scrollbar space-y-3">
        {items.map((item) => (
          <div key={item.id} className="rounded-[1.35rem] border border-white/10 bg-white/[0.03] p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-xs uppercase tracking-[0.25em] font-orbitron text-cyan-300">{item.kind}</div>
                <div className="mt-2 text-white">{item.content}</div>
              </div>
              <button
                onClick={() => api.forget(item.id).then(load)}
                className="text-white/45 hover:text-red-300 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
        {items.length === 0 && <div className="text-white/45">No persistent memories saved yet.</div>}
      </div>
    </div>
  );
};

export default MemoryViewer;
