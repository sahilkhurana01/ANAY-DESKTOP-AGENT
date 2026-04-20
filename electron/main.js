const path = require("path");
const fs = require("fs");
const { app, BrowserWindow, globalShortcut, ipcMain } = require("electron");
const Store = require("electron-store");
const { spawn } = require("child_process");
const { createTray } = require("./tray");

function resolvePythonExecutable() {
  const rootDir = path.join(__dirname, "..");
  const candidates = [
    process.env.ANAY_BACKEND_PYTHON,
    path.join(rootDir, ".venv312", "Scripts", "python.exe"),
    path.join(rootDir, "backend", ".venv312", "Scripts", "python.exe"),
    process.platform === "win32" ? "py" : "python3",
    "python",
  ].filter(Boolean);
  for (const c of candidates) {
    if (c.endsWith(".exe") && !fs.existsSync(c)) continue;
    return c;
  }
  return "python";
}

const store = new Store({
  defaults: {
    alwaysOnTop: true,
    launchOnStartup: false,
    useLocalFrontend: true,
    frontendUrl: "http://127.0.0.1:5173",
    backendUrl: "http://127.0.0.1:8000"
  }
});

let mainWindow;
let tray;
let backendProcess;

function createMainWindow() {
  const settings = store.store;
  mainWindow = new BrowserWindow({
    width: 1320,
    height: 860,
    minWidth: 980,
    minHeight: 640,
    frame: false,
    /* Opaque background: transparent + #00000000 often renders as a blank window on Windows. */
    transparent: false,
    show: false,
    alwaysOnTop: settings.alwaysOnTop,
    backgroundColor: "#080808",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  const distHtml = path.join(__dirname, "..", "frontend", "dist", "index.html");
  if (app.isPackaged) {
    mainWindow.loadFile(distHtml);
  } else {
    mainWindow.loadURL(settings.frontendUrl);
  }
  mainWindow.once("ready-to-show", () => mainWindow.show());
  mainWindow.on("blur", () => {
    if (!app.isPackaged) return;
    if (!mainWindow.webContents.isDevToolsOpened()) {
      mainWindow.hide();
    }
  });
}

function toggleWindow() {
  if (!mainWindow) return;
  if (mainWindow.isVisible()) {
    mainWindow.hide();
  } else {
    mainWindow.show();
    mainWindow.focus();
  }
}

function startBackend() {
  if (backendProcess || !app.isPackaged) return;
  const rootDir = path.join(__dirname, "..");
  const python = resolvePythonExecutable();
  const baseArgs = [
    "-m",
    "uvicorn",
    "main:app",
    "--app-dir",
    "backend",
    "--host",
    "127.0.0.1",
    "--port",
    "8000",
  ];
  const command = python === "py" ? "py" : python;
  const args = python === "py" ? ["-3.12", ...baseArgs] : baseArgs;

  backendProcess = spawn(command, args, {
    cwd: rootDir,
    env: {
      ...process.env,
      PYTHONIOENCODING: "utf-8",
    },
    windowsHide: true,
  });

  backendProcess.stdout?.on("data", (data) => console.log(`[backend] ${data}`));
  backendProcess.stderr?.on("data", (data) => console.error(`[backend] ${data}`));
}

function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

function wireIpc() {
  ipcMain.handle("anay:get-settings", () => store.store);
  ipcMain.handle("anay:set-settings", (_event, patch) => {
    const next = { ...store.store, ...patch };
    store.set(next);
    if (mainWindow) {
      mainWindow.setAlwaysOnTop(Boolean(next.alwaysOnTop));
    }
    return next;
  });
  ipcMain.handle("anay:toggle-always-on-top", () => {
    const nextValue = !store.get("alwaysOnTop");
    store.set("alwaysOnTop", nextValue);
    mainWindow?.setAlwaysOnTop(nextValue);
    return { alwaysOnTop: nextValue };
  });
  ipcMain.handle("anay:toggle-launch-on-startup", () => {
    const nextValue = !store.get("launchOnStartup");
    store.set("launchOnStartup", nextValue);
    app.setLoginItemSettings({ openAtLogin: nextValue });
    return { launchOnStartup: nextValue };
  });
  ipcMain.handle("anay:hide-window", () => {
    mainWindow?.hide();
    return { hidden: true };
  });
  ipcMain.handle("anay:minimize-window", () => {
    mainWindow?.minimize();
    return { minimized: true };
  });
  ipcMain.handle("anay:maximize-window", () => {
    if (mainWindow?.isMaximized()) {
      mainWindow.unmaximize();
      return { maximized: false };
    } else {
      mainWindow.maximize();
      return { maximized: true };
    }
  });
}

app.whenReady().then(() => {
  startBackend();
  createMainWindow();
  wireIpc();

  globalShortcut.register("CommandOrControl+Space", toggleWindow);
  tray = createTray({
    app,
    onToggle: toggleWindow,
    onQuit: () => app.quit(),
    iconPath: path.join(__dirname, "assets", "trayTemplate.png")
  });
});

app.on("before-quit", () => {
  stopBackend();
  globalShortcut.unregisterAll();
  tray?.destroy();
});

app.on("window-all-closed", (event) => {
  event.preventDefault();
});
