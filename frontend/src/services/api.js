// frontend/src/services/api.js
import axios from "axios";

// ================================
// BASE URL (VITE)
// ================================
const baseURL = import.meta.env.VITE_API_URL;

// Blindagem: avisa claramente se o .env não foi carregado
if (!baseURL) {
  console.error(
    "❌ ERRO CRÍTICO: VITE_API_URL não definida. Verifique frontend/.env e reinicie o Vite."
  );
} else {
  console.log("✅ API BaseURL:", baseURL);
}

// ================================
// AXIOS INSTANCE
// ================================
const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

// ================================
// REQUEST INTERCEPTOR (TOKEN)
// ================================
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ================================
// RESPONSE INTERCEPTOR (LOG + AUTH)
// ================================
api.interceptors.response.use(
  (response) => {
    console.log(
      `✅ ${response.config.method?.toUpperCase()} ${response.config.url}`,
      response.status
    );
    return response;
  },
  (error) => {
    const status = error.response?.status;
    const url = error.config?.url;

    console.error(`❌ API ERROR ${status || ""} ${url || ""}`);

    // Token expirado / inválido
    if (status === 401) {
      console.warn("⚠️ Token inválido ou expirado. Redirecionando para login.");
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

export default api;
