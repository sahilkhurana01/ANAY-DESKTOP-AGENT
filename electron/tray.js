const { nativeImage, Tray, Menu } = require("electron");

function createTray({ app, onToggle, onQuit, iconPath }) {
  const icon = nativeImage.createFromPath(iconPath);
  const tray = new Tray(icon.isEmpty() ? nativeImage.createEmpty() : icon);
  tray.setToolTip("ANAY Desktop");
  tray.setContextMenu(
    Menu.buildFromTemplate([
      { label: "Show / Hide ANAY", click: onToggle },
      { type: "separator" },
      { label: "Quit", click: onQuit },
    ])
  );
  tray.on("click", onToggle);
  return tray;
}

module.exports = { createTray };
