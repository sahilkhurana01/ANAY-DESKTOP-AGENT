const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("anayDesktop", {
  getSettings: () => ipcRenderer.invoke("anay:get-settings"),
  setSettings: (patch) => ipcRenderer.invoke("anay:set-settings", patch),
  toggleAlwaysOnTop: () => ipcRenderer.invoke("anay:toggle-always-on-top"),
  toggleLaunchOnStartup: () => ipcRenderer.invoke("anay:toggle-launch-on-startup"),
  hideWindow: () => ipcRenderer.invoke("anay:hide-window"),
  minimizeWindow: () => ipcRenderer.invoke("anay:minimize-window"),
  maximizeWindow: () => ipcRenderer.invoke("anay:maximize-window"),
  platform: process.platform,
});
