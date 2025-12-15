// E:\MAWDSLEYS-AGENTE\frontend\src\services\api.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api", // 🔥 ADICIONE /api AQUI!
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

// Injeta token SOMENTE se existir
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor de resposta MELHORADO
api.interceptors.response.use(
  (res) => {
    console.log(
      `✅ ${res.config.method?.toUpperCase()} ${res.config.url}:`,
      res.status
    );
    return res;
  },
  (err) => {
    console.error(
      `❌ ${err.config?.method?.toUpperCase()} ${err.config?.url}:`,
      err.response?.status
    );

    // Token expirado
    if (err.response?.status === 401) {
      console.warn("Token expirado ou inválido");
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }

    return Promise.reject(err);
  }
);

export default api;
