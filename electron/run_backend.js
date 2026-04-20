const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const rootDir = path.resolve(__dirname, "..");
const candidates = [
  process.env.ANAY_BACKEND_PYTHON,
  path.join(rootDir, ".venv312", "Scripts", "python.exe"),
  path.join(rootDir, "backend", ".venv312", "Scripts", "python.exe"),
  process.platform === "win32" ? "py" : "python3",
  "python",
].filter(Boolean);

function trySpawn(index = 0) {
  if (index >= candidates.length) {
    console.error("No usable Python runtime found for ANAY backend.");
    process.exit(1);
  }

  const candidate = candidates[index];
  if (candidate.endsWith(".exe") && !fs.existsSync(candidate)) {
    return trySpawn(index + 1);
  }

  const command = candidate === "py" ? "py" : candidate;
  const args = candidate === "py" ? ["-3.12"] : [];
  const child = spawn(
    command,
    [...args, "-m", "uvicorn", "main:app", "--app-dir", "backend", "--host", "127.0.0.1", "--port", "8000", "--reload"],
    {
      cwd: rootDir,
      stdio: "inherit",
      shell: false,
      env: {
        ...process.env,
        PYTHONIOENCODING: "utf-8",
      },
    }
  );

  child.on("error", () => trySpawn(index + 1));
  child.on("exit", (code) => process.exit(code || 0));
}

trySpawn();
