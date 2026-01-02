// frontend/src/services/api.js
import axios from "axios";

// ================================
// BASE URL (VITE)
// ================================
const baseURL = import.meta.env.VITE_API_URL;

if (!baseURL) {
  console.error(
    "❌ ERRO CRÍTICO: VITE_API_URL não definida. Verifique frontend/.env"
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
// RESPONSE INTERCEPTOR
// ================================
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;

    if (status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

export default api;
