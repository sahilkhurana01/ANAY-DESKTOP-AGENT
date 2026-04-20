/// <reference types="vite/client" />

interface AnayDesktopBridge {
  getSettings?: () => Promise<Record<string, unknown>>;
  setSettings?: (patch: Record<string, unknown>) => Promise<Record<string, unknown>>;
  toggleAlwaysOnTop?: () => Promise<{ alwaysOnTop: boolean }>;
  toggleLaunchOnStartup?: () => Promise<{ launchOnStartup: boolean }>;
  hideWindow?: () => Promise<{ hidden: boolean }>;
  platform?: string;
}

interface Window {
  anayDesktop?: AnayDesktopBridge;
}
