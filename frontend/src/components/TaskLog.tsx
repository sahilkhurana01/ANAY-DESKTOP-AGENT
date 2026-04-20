import { useEffect, useState } from "react";
import { PauseCircle, PlayCircle } from "lucide-react";

import { AgentTask, api } from "@/lib/api";

const TaskLog = () => {
  const [tasks, setTasks] = useState<AgentTask[]>([]);
  const [draft, setDraft] = useState("");

  const loadTasks = async () => {
    try {
      const data = await api.getTasks();
      setTasks(data.tasks);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    loadTasks();
    const timer = window.setInterval(loadTasks, 4000);
    return () => window.clearInterval(timer);
  }, []);

  const createTask = async () => {
    if (!draft.trim()) return;
    await api.createTask("Desktop objective", draft.trim());
    setDraft("");
    loadTasks();
  };

  return (
    <div className="anay-panel h-full p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-orbitron text-xs tracking-[0.35em] text-primary uppercase">Agent Queue</p>
          <h3 className="text-2xl font-orbitron font-black text-white">Task Log</h3>
        </div>
        <div className="px-3 py-1 rounded-full bg-white/5 text-white/70 text-xs font-orbitron border border-white/10">
          {tasks.length} tracked
        </div>
      </div>

      <div className="rounded-[1.35rem] border border-white/10 bg-black/20 p-3 flex gap-2">
        <input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Research X, open tools, save report..."
          className="flex-1 bg-transparent outline-none text-white placeholder:text-white/35"
        />
        <button onClick={createTask} className="anay-button-primary px-4 py-2 text-sm">
          Queue
        </button>
      </div>

      <div className="flex-1 overflow-auto custom-scrollbar space-y-3">
        {tasks.map((task) => (
          <div key={task.id} className="rounded-[1.35rem] border border-white/10 bg-white/[0.03] p-4 space-y-3">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-white font-semibold">{task.title}</div>
                <div className="text-white/45 text-sm">{task.summary || task.objective}</div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase font-orbitron tracking-[0.2em] text-cyan-300">{task.status}</span>
                {task.status === "running" ? (
                  <button onClick={() => api.cancelTask(task.id).then(loadTasks)} className="text-amber-300">
                    <PauseCircle className="w-4 h-4" />
                  </button>
                ) : (
                  <PlayCircle className="w-4 h-4 text-emerald-300" />
                )}
              </div>
            </div>
            <div className="space-y-2">
              {(task.logs || []).slice(-3).map((log) => (
                <div key={`${task.id}-${log.timestamp}`} className="text-sm text-white/65 border-l border-cyan-400/30 pl-3">
                  {log.message}
                </div>
              ))}
            </div>
          </div>
        ))}
        {tasks.length === 0 && <div className="text-white/45">No autonomous tasks yet.</div>}
      </div>
    </div>
  );
};

export default TaskLog;
