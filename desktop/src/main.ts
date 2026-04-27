import "./style.css";
import { Command } from "@tauri-apps/plugin-shell";

const POS_URL = "http://127.0.0.1:8765";
const statusNode = document.getElementById("status");

function setStatus(message: string) {
  if (statusNode) statusNode.textContent = message;
}

async function waitForServer(): Promise<void> {
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    try {
      await fetch(`${POS_URL}/health/`, { cache: "no-store" });
      return;
    } catch (_error) {
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  }
  throw new Error("No se pudo iniciar el servidor local.");
}

async function boot() {
  setStatus("Arrancando base local...");
  const command = Command.sidecar("binaries/cauloti_server");
  await command.spawn();
  setStatus("Preparando interfaz...");
  await waitForServer();
  window.location.replace(POS_URL);
}

boot().catch((error) => {
  setStatus(error instanceof Error ? error.message : "Error al iniciar.");
});

