import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Ports come from dev.sh (VITE_API_PORT / VITE_UI_PORT) with sane defaults,
// so a busy port doesn't hard-fail. Vite itself bumps the UI port when taken.
const apiPort = process.env.VITE_API_PORT || "8765";
const uiPort = Number(process.env.VITE_UI_PORT || "5173");

export default defineConfig({
  plugins: [react()],
  server: {
    port: uiPort,
    proxy: {
      "/api": {
        target: `http://127.0.0.1:${apiPort}`,
        changeOrigin: true,
      },
    },
  },
});
