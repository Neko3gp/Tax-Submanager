import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En local el backend está en :8000; con Docker se apunta a http://backend:8000 (VITE_API_PROXY).
const target = process.env.VITE_API_PROXY || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target, changeOrigin: true },
    },
  },
});
