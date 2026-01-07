// frontend/src/services/api.js
import axios from "axios";

// ================================
// BASE URL DO BACKEND NO FLY.IO (FIXA)
// ================================
const baseURL = "https://backend-silent-snowflake-7300.fly.dev";

// Debug
console.log("✅ API BaseURL configurada:", baseURL);

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

// ================================
// FUNÇÕES ESPECÍFICAS PARA ADMIN FIXO
// ================================

// Admin login fixo para Nelson e Daniela
export const adminLogin = async (email, password) => {
  try {
    console.log("🔐 Tentando admin login fixo:", email);
    
    // Usa o endpoint admin-login do backend
    const response = await api.post("/api/v1/auth/admin-login", {
      email,
      password,
    });
    
    // Salva token e user
    const { access_token, user } = response.data;
    localStorage.setItem("token", access_token);
    localStorage.setItem("user", JSON.stringify(user));
    
    // Configura header para próximas requisições
    api.defaults.headers.common.Authorization = `Bearer ${access_token}`;
    
    console.log("✅ Admin login successful:", user.name);
    return { success: true, user };
    
  } catch (error) {
    console.error("❌ Admin login failed:", error.response?.data || error.message);
    return { 
      success: false, 
      error: error.response?.data?.detail || "Credenciais inválidas" 
    };
  }
};

// Testar conexão com backend
export const testBackendConnection = async () => {
  try {
    const response = await api.get("/health");
    return {
      connected: true,
      status: response.data.status,
      openai: response.data.openai
    };
  } catch (error) {
    return {
      connected: false,
      error: error.message
    };
  }
};

export default api;
export { baseURL };