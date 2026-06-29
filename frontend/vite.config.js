import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    allowedHosts: "all",
    proxy: {
      "/api": { target: "https://aegis-api.onrender.com", changeOrigin: true },
      "/v1": { target: "https://aegis-api.onrender.com", changeOrigin: true },
      "/health": { target: "https://aegis-api.onrender.com", changeOrigin: true },
      "/ready": { target: "https://aegis-api.onrender.com", changeOrigin: true },
      "/ws": { target: "wss://aegis-api.onrender.com", ws: true },
    },
  },
})
