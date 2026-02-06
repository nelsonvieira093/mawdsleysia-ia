// frontend/src/services/api.js
import axios from "axios";

// =====================================================
// CONFIGURAÇÃO BASE
// =====================================================

// ✅ Base do backend via variável de ambiente (Vercel / Vite)
// 🔒 Blindado: NUNCA usa localhost em produção
export const baseURL = import.meta.env.VITE_API_URL || 
  (import.meta.env.MODE === "development" 
    ? "http://localhost:8080" 
    : "https://backend-silent-snowflake-7300.fly.dev");

// Instância única do Axios
const api = axios.create({
  baseURL,
  timeout: 30000, // ⏱️ aumentado para evitar falso "backend offline"
  headers: {
    "Content-Type": "application/json",
  },
});

// =====================================================
// INTERCEPTORS
// =====================================================

// 🔐 Adiciona token automaticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// 🚪 Trata erro 401 global (sessão expirada)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

// =====================================================
// BACKEND / HEALTH CHECK
// =====================================================

// ✅ Health check leve e confiável (NÃO usar openapi.json)
export const testBackendConnection = async () => {
  try {
    const response = await api.get("/health", { timeout: 10000 });
    return { connected: response.status === 200 };
  } catch (error) {
    return { connected: false, error: error.message };
  }
};

// =====================================================
// AUTH
// =====================================================

export const adminLogin = async (email, password) => {
  try {
    const response = await api.post("/api/v1/auth/admin-login", {
      email,
      password,
    });

    const tokenData = response.data;
    const access_token = tokenData.access_token || tokenData.token;

    if (!access_token) {
      throw new Error("Token não retornado pelo servidor");
    }

    const user = tokenData.user;

    localStorage.setItem("token", access_token);
    localStorage.setItem("user", JSON.stringify(user));
    api.defaults.headers.common.Authorization = `Bearer ${access_token}`;

    return { success: true, user, access_token };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || "Credenciais inválidas",
    };
  }
};

// =====================================================
// AUTOMAÇÕES
// =====================================================

export const checkWeeklyMeetings = async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    throw new Error("Token ausente. Faça login novamente.");
  }

  const response = await api.post(
    "/api/v1/automations/check-weekly-meetings",
    {},
  );
  return response.data;
};

// =====================================================
// IA / CONTEXTO
// =====================================================

const getCurrentUserId = () => {
  try {
    const userStr = localStorage.getItem("user");
    if (!userStr) return 1;
    const user = JSON.parse(userStr);
    return user.id || 1;
  } catch {
    return 1;
  }
};

export const getAIContext = async (userId = null) => {
  const targetUserId = userId || getCurrentUserId();

  const [followups, notes, meetings, kpis] = await Promise.allSettled([
    api.get("/api/followups/"),
    api.get("/api/notes/"),
    api.get("/api/meetings/"),
    api.get("/api/kpis/overview"),
  ]);

  return {
    user_id: targetUserId,
    followups: followups.status === "fulfilled" ? followups.value.data : [],
    notes: notes.status === "fulfilled" ? notes.value.data : [],
    meetings: meetings.status === "fulfilled" ? meetings.value.data : [],
    kpis: kpis.status === "fulfilled" ? kpis.value.data : null,
    timestamp: new Date().toISOString(),
  };
};

// 👈 Exportado apenas uma vez
export const refreshAIContext = async () => {
  return getAIContext();
};

// =====================================================
// CHAT IA
// =====================================================

export const chatWithAI = async (message) => {
  try {
    const response = await api.post("/api/v1/chat", {
      message,
      timestamp: new Date().toISOString(),
    });

    return {
      success: true,
      response:
        response.data.reply || response.data.response || response.data.message,
      raw: response.data,
    };
  } catch (error) {
    return {
      success: false,
      response: "Serviço de IA indisponível no momento.",
      error: error.message,
    };
  }
};

// =====================================================
// BUSCA INTELIGENTE
// =====================================================

export const smartSearch = async (query) => {
  const [followups, notes, meetings] = await Promise.allSettled([
    api.get("/api/followups/"),
    api.get("/api/notes/"),
    api.get("/api/meetings/"),
  ]);

  const normalize = (res) => (res.status === "fulfilled" ? res.value.data : []);

  const f = normalize(followups).filter((i) =>
    JSON.stringify(i).toLowerCase().includes(query.toLowerCase()),
  );
  const n = normalize(notes).filter((i) =>
    JSON.stringify(i).toLowerCase().includes(query.toLowerCase()),
  );
  const m = normalize(meetings).filter((i) =>
    JSON.stringify(i).toLowerCase().includes(query.toLowerCase()),
  );

  return {
    query,
    followups: f,
    notes: n,
    meetings: m,
    total: f.length + n.length + m.length,
  };
};

// =====================================================
// FOLLOWUPS VIA IA
// =====================================================

export const createFollowupViaAI = async (data) => {
  const response = await api.post("/api/followups/", data);
  return {
    success: true,
    data: response.data,
  };
};

// =====================================================
// BULLET JOURNAL EXECUTIVO
// =====================================================

// 📘 Bullet Journal é apenas um MODO do chat.
export async function captureExecutive(input) {
  const response = await api.post("/api/v1/chat", {
    message: input,
    mode: "bullet_journal_ceo",
    timestamp: new Date().toISOString(),
  });

  return {
    success: true,
    response:
      response.data.reply || response.data.response || response.data.message,
    raw: response.data,
  };
}

// =====================================================
// 📘 HISTÓRICO DO BULLET JOURNAL (⬅️ CORREÇÃO DO ERRO)
// =====================================================

export const getExecutiveJournals = async () => {
  const response = await api.get("/api/executive-journals");
  return response.data;
};

// =====================================================
// EXPORT DEFAULT
// =====================================================

export default api;
