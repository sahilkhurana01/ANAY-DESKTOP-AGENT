import { useCallback, useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";

import { api } from "@/lib/api";
import { ANAYWebSocket, ServerMessage } from "@/lib/websocket";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  reasoning?: string;
}

interface StoredMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  reasoning?: string;
}

/** Pure helper — no hooks, safe to call anywhere. */
function normalizeAssistantText(text: string): string {
  const trimmed = text.trim();
  if (!trimmed) return "No response received.";

  try {
    const parsed = JSON.parse(trimmed) as { detail?: string; message?: string };
    if (parsed?.detail === "Not Found") {
      return "The local backend endpoint is not responding correctly yet. Check that ANAY's backend modules finished starting, then try again.";
    }
    if (typeof parsed?.detail === "string") return parsed.detail;
    if (typeof parsed?.message === "string") return parsed.message;
  } catch {
    // fall through to raw text
  }

  return trimmed;
}

/** Robust deduplication check */
function isDuplicate(prev: Message[], role: string, content: string, reasoning?: string): boolean {
  const now = Date.now();
  // Compare strings after normalization (trim and same reasoning)
  const normContent = content.trim();
  
  return prev.some((item) => {
    if (item.role !== role) return false;
    
    // Check if contents match (ignoring whitespace)
    if (item.content.trim() !== normContent) return false;
    
    // Check reasoning (standardize null/undefined to empty string)
    if ((item.reasoning || "") !== (reasoning || "")) return false;
    
    // Check if it happened within a 5-second window
    return Math.abs(now - item.timestamp.getTime()) < 5000;
  });
}

export const useAnayChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const abortControllerRef = useState(() => new AbortController())[0]; 
  // Note: Using a simple ref-like state or separate ref would be better but keeping it simple.
  // Actually, let's use a proper useRef approach.
  const [currentAbortController, setCurrentAbortController] = useState<AbortController | null>(null);

  useEffect(() => {
    const savedMessages = localStorage.getItem("chatHistory");
    if (!savedMessages) return;
    try {
      const parsed = JSON.parse(savedMessages) as StoredMessage[];
      setMessages(parsed.map((item) => ({ ...item, timestamp: new Date(item.timestamp) })));
    } catch (error) {
      console.error(error);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(
      "chatHistory",
      JSON.stringify(messages.map((item) => ({ ...item, timestamp: item.timestamp.toISOString() })))
    );
  }, [messages]);

  useEffect(() => {
    const ws = ANAYWebSocket.getInstance(import.meta.env.VITE_WS_URL || "ws://127.0.0.1:8000/ws");

    const handleOpen = () => setIsConnected(true);
    const handleClose = () => setIsConnected(false);
    const push = (role: "user" | "assistant", content: string, reasoning?: string) => {
      const normContent = normalizeAssistantText(content);
      if (!normContent) return;
      
      setMessages((prev) => {
        if (isDuplicate(prev, role, normContent, reasoning)) return prev;
        return [...prev, { id: uuidv4(), role, content: normContent, timestamp: new Date(), reasoning }];
      });
    };

    const handleUser = (data: ServerMessage) => {
      if (data.type === "user_message") push("user", data.content || data.message || data.text || "");
    };
    const handleTranscript = (data: ServerMessage) => {
      if (data.type === "final_transcript") push("user", data.payload || data.text || "");
    };
    const handleResponse = (data: ServerMessage) => {
      if (data.type === "response") {
        const reasoning = data.reasoning || (data.meta as any)?.reasoning || "";
        push("assistant", data.content || data.message || data.text || "", reasoning);
        setIsProcessing(false);
      }
    };

    ws.on("open", handleOpen);
    ws.on("close", handleClose);
    ws.on("user_message", handleUser);
    ws.on("final_transcript", handleTranscript);
    ws.on("response", handleResponse);
    ws.connect().catch(console.error);

    api.healthCheck().then(() => setIsConnected(true)).catch(() => setIsConnected(false));

    return () => {
      ws.off("open", handleOpen);
      ws.off("close", handleClose);
      ws.off("user_message", handleUser);
      ws.off("final_transcript", handleTranscript);
      ws.off("response", handleResponse);
    };
  }, []);

  const stopGeneration = useCallback(() => {
    if (currentAbortController) {
      currentAbortController.abort();
      setCurrentAbortController(null);
    }
    setIsProcessing(false);
  }, [currentAbortController]);

  const sendMessage = useCallback(async (userMessage: string, forceModel?: string): Promise<string> => {
    if (!userMessage.trim()) return "";

    const userEntry: Message = {
      id: uuidv4(),
      role: "user",
      content: userMessage,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userEntry]);
    setIsProcessing(true);

    const controller = new AbortController();
    setCurrentAbortController(controller);

    try {
      const model = forceModel || localStorage.getItem("anay:model") || "auto";
      const offline = localStorage.getItem("anay:offline") === "true";
      const response = await api.requestChat?.(userMessage, model, offline, controller.signal);
      const text = normalizeAssistantText(response?.text || "No response received.");
      const reasoning = response?.reasoning || "";
      
      setMessages((prev) => {
        if (isDuplicate(prev, "assistant", text, reasoning)) return prev;
        return [
          ...prev,
          { id: uuidv4(), role: "assistant", content: text, timestamp: new Date(), reasoning },
        ];
      });
      return text;
    } catch (error: any) {
      if (error.name === "AbortError") {
        console.log("Request aborted");
        return "";
      }
      const text = normalizeAssistantText(error instanceof Error ? error.message : "Failed to send message.");
      setMessages((prev) => [
        ...prev,
        { id: uuidv4(), role: "assistant", content: text, timestamp: new Date() },
      ]);
      return text;
    } finally {
      setIsProcessing(false);
      setCurrentAbortController(null);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    localStorage.removeItem("chatHistory");
  }, []);

  return { messages, isProcessing, isConnected, sendMessage, clearMessages, stopGeneration };
};
