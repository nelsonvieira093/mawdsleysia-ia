import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // 🔥 ADICIONE ESTE BLOCO PARA REDIRECIONAR /auth PARA /api/auth
      "/auth": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/auth/, "/api/auth"),
      },
    },
  },
});
