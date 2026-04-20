const API_BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed for ${path}`);
  }
  return response.json();
}

export interface DesktopState {
  system: {
    cpu_percent: number;
    ram_percent: number;
    disk_percent: number;
    battery_percent?: number | null;
    battery_plugged?: boolean | null;
    /** @deprecated prefer battery_percent */
    battery?: number | string;
    charging?: boolean | string;
    platform: string;
    hostname: string;
    uptime_seconds?: number;
    ram_used_gb?: number;
  };
  voice: { deepgram: boolean; elevenlabs: boolean; voice_id?: string | null; mode: string };
  wake_word: { enabled: boolean; engine: string; wake_phrase: string };
  models: { default: string; available: string[] };
  runtime_settings: {
    default_model: string;
    offline_mode: boolean;
    voice_mode: string;
    tts_enabled: boolean;
  };
  memory: { recent: MemoryItem[]; reminders: ReminderItem[] };
  tasks: AgentTask[];
}

export interface MemoryItem {
  id: string;
  kind: string;
  content: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface ReminderItem {
  id: string;
  task: string;
  due_at: string;
  status: string;
  created_at: string;
}

export interface AgentTask {
  id: string;
  title: string;
  objective?: string;
  status: string;
  summary?: string | null;
  logs?: Array<{ timestamp: string; message: string }>;
  created_at: string;
  updated_at: string;
}

export const api = {
  healthCheck: () => request<{ status: string; timestamp: string | null }>("/health"),
  requestChat: (message: string, model = "auto", offline = false, signal?: AbortSignal) =>
    request<{ provider: string; model: string; text: string; reasoning?: string; tool_calls: unknown[] }>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, model, offline }),
      signal
    }),
  getDesktopState: () => request<DesktopState>("/api/desktop/state"),
  getSettings: () =>
    request<{ default_model: string; offline_mode: boolean; voice_mode: string; tts_enabled: boolean }>("/api/settings"),
  updateSettings: (patch: { default_model?: string; offline_mode?: boolean; voice_mode?: string; tts_enabled?: boolean }) =>
    request<{ default_model: string; offline_mode: boolean; voice_mode: string; tts_enabled: boolean }>("/api/settings", {
      method: "POST",
      body: JSON.stringify(patch),
    }),
  getMemory: () => request<{ items: MemoryItem[]; reminders: ReminderItem[] }>("/api/memory"),
  remember: (content: string, kind = "note") =>
    request<{ item: MemoryItem }>("/api/memory/remember", {
      method: "POST",
      body: JSON.stringify({ content, kind }),
    }),
  forget: (memoryId: string) =>
    request<{ deleted: boolean }>(`/api/memory/${memoryId}`, { method: "DELETE" }),
  getTasks: () => request<{ tasks: AgentTask[] }>("/api/agent/tasks"),
  createTask: (title: string, objective: string) =>
    request<{ task: AgentTask }>("/api/agent/tasks", {
      method: "POST",
      body: JSON.stringify({ title, objective }),
    }),
  cancelTask: (taskId: string) =>
    request<{ task: AgentTask }>(`/api/agent/tasks/${taskId}/cancel`, { method: "POST" }),
  inspectScreen: (prompt: string) =>
    request<{ analysis: string; provider: string; screenshot_base64: string }>("/api/vision/inspect", {
      method: "POST",
      body: JSON.stringify({ prompt }),
    }),
  getTools: () => request<{ tools: Array<{ name: string; description: string }> }>("/api/tools"),
  getContacts: () => request<Array<{ name: string; phone: string; updated_at: string }>>("/api/contacts"),
  addContact: (name: string, phone: string) =>
    request<{ status: string }>("/api/contacts", {
      method: "POST",
      body: JSON.stringify({ name, phone }),
    }),
  deleteContact: (name: string) =>
    request<{ status: string }>(`/api/contacts/${name}`, { method: "DELETE" }),
};
