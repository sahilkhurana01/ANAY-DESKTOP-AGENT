/** WebSocket client wrapper for ANAY backend communication */
export type WebSocketMessage =
  | { type: 'message'; content: string }
  | { type: 'audio_chunk'; payload: string }
  | { type: 'text_input'; payload: string }
  | { type: 'status'; status: 'listening' | 'speaking' | 'idle' | 'processing' }
  | { type: 'audio_level'; level: number }
  | { type: 'request_metrics' };

export type ServerMessage =
  | { type: 'response'; content: string; message?: string; text?: string }
  | { type: 'system_action'; action: string; result: any }
  | { type: 'status'; status: string }
  | { type: 'error'; message: string }
  | { type: 'partial_transcript'; payload: string; text?: string }
  | { type: 'final_transcript'; payload: string; text?: string }
  | { type: 'user_message'; content: string; message?: string; text?: string; role?: string }
  | { type: 'transcript'; text: string; payload?: string }
  | { type: 'ai_message'; content: string; text?: string }
  | { type: 'ai_text'; payload: string }
  | { type: 'tts_audio'; payload: string; audio?: string }
  | { type: 'audio_chunk'; audio: string }
  | { type: 'audio_level'; payload: number }
  | { type: 'system_metrics'; data: any };

export class ANAYWebSocket {
  private static instance: ANAYWebSocket | null = null;
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private isConnecting = false;
  private shouldReconnect = true;

  constructor(url: string = 'ws://localhost:8000/ws') {
    this.url = url;
  }

  public static getInstance(url?: string): ANAYWebSocket {
    if (!ANAYWebSocket.instance) {
      ANAYWebSocket.instance = new ANAYWebSocket(url);
    }
    return ANAYWebSocket.instance;
  }

  connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return Promise.resolve();
    }

    if (this.isConnecting) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      this.isConnecting = true;

      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.emit('open', {});
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data: ServerMessage = JSON.parse(event.data);
            console.log('📨 WebSocket message received:', data.type, data);
            this.emit('message', data);
            this.emit(data.type, data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error, event.data);
          }
        };

        this.ws.onerror = (error) => {
          this.isConnecting = false;
          this.emit('error', { error });
          reject(error);
        };

        this.ws.onclose = () => {
          this.isConnecting = false;
          this.emit('close', {});

          if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
              this.connect().catch(console.error);
            }, this.reconnectDelay * this.reconnectAttempts);
          }
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.shouldReconnect = false;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Attempting to connect...');
      this.connect().then(() => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify(message));
        }
      }).catch(console.error);
    }
  }

  on(event: string, callback: (data: any) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  off(event: string, callback: (data: any) => void): void {
    this.listeners.get(event)?.delete(callback);
  }

  private emit(event: string, data: any): void {
    this.listeners.get(event)?.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in event listener for ${event}:`, error);
      }
    });
  }

  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
