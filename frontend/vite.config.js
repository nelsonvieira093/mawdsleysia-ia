import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    host: true, // 🔥 aceita conexões externas (Cloudflare)
    port: 5173,
    strictPort: true,

    // 🔐 Libera hosts do Cloudflare Tunnel
    allowedHosts: [".trycloudflare.com", "localhost", "127.0.0.1"],

    // 🔁 Proxy para o backend (LOCAL)
    proxy: {
      // /auth  -> /api/auth
      "/auth": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/auth/, "/api/auth"),
      },

      // /api -> backend direto
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
