// frontend/src/services/api.js
import axios from "axios";

// =====================================================
// CONFIGURAÇÃO BASE - PRODUÇÃO DEFINITIVA
// =====================================================

// ✅ URL FIXA DE PRODUÇÃO - COM FALLBACK DINÂMICO
const getBaseURL = () => {
  // Prioridade 1: URL fixa de produção
  const productionURL = "https://backend-silent-snowflake-7300.fly.dev";
  
  // Prioridade 2: Variável de ambiente (se disponível)
  try {
    // Acessa import.meta.env dinamicamente para evitar erros de parse em bundlers que não aceitam o token "import"
    const getViteEnv = new Function(
      'return (typeof import.meta !== "undefined" && import.meta && import.meta.env && import.meta.env.VITE_API_URL) || undefined;'
    );
    const envURL = getViteEnv();
    if (envURL && envURL !== 'undefined' && envURL.startsWith('http')) {
      console.log('🔧 Usando VITE_API_URL:', envURL);
      return envURL;
    }
  } catch (e) {
    // import.meta não disponível ou acessível — continua para próxima prioridade
  }
  
  // Prioridade 3: Configuração global window
  if (typeof window !== 'undefined' && window.APP_CONFIG && window.APP_CONFIG.API_URL) {
    console.log('🔧 Usando window.APP_CONFIG:', window.APP_CONFIG.API_URL);
    return window.APP_CONFIG.API_URL;
  }
  
  // Fallback: URL de produção padrão
  console.log('🚀 Usando URL de produção padrão:', productionURL);
  return productionURL;
};

export const baseURL = getBaseURL();

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
// BACKEND / HEALTH CHECK - CORRIGIDO
// =====================================================

// ✅ Health check com tratamento de erro melhorado
export const testBackendConnection = async () => {
  try {
    console.log('🔍 Testando conexão com:', baseURL);
    
    // Usa o axios instance diretamente
    const response = await api.get("/health", { timeout: 10000 });
    
    console.log('✅ Backend conectado:', response.status);
    return { 
      connected: true, 
      status: response.status,
      data: response.data 
    };
  } catch (error) {
    console.error('❌ Erro na conexão:', {
      message: error.message,
      code: error.code,
      url: baseURL
    });
    
    // Tenta fallback com fetch direto
    try {
      const fetchResponse = await fetch(`${baseURL}/health`, {
        method: 'GET',
        mode: 'cors',
        headers: { 'Accept': 'application/json' }
      });
      
      if (fetchResponse.ok) {
        const data = await fetchResponse.json();
        console.log('✅ Conexão via fetch funcionou');
        return { connected: true, status: fetchResponse.status, data };
      }
    } catch (fetchError) {
      console.error('❌ Fallback fetch também falhou:', fetchError);
    }
    
    return { 
      connected: false, 
      error: error.message,
      code: error.code,
      url: baseURL
    };
  }
};

// =====================================================
// AUTH
// =====================================================

export const adminLogin = async (email, password) => {
  try {
    console.log('🔐 Tentando login em:', `${baseURL}/api/v1/auth/admin-login`);
    
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

    console.log('✅ Login bem-sucedido para:', email);
    return { success: true, user, access_token };
  } catch (error) {
    console.error('❌ Erro no login:', {
      error: error.message,
      response: error.response?.data
    });
    
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

  try {
    const response = await api.post(
      "/api/v1/automations/check-weekly-meetings",
      {},
    );
    return response.data;
  } catch (error) {
    console.error('❌ Erro em checkWeeklyMeetings:', error);
    throw error;
  }
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

  try {
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
  } catch (error) {
    console.error('❌ Erro ao buscar contexto IA:', error);
    throw error;
  }
};

// 👈 Exportado apenas uma vez
export const refreshAIContext = async () => {
  return getAIContext();
};

// =====================================================
// CHAT IA - CORRIGIDO
// =====================================================

export const chatWithAI = async (message) => {
  try {
    console.log('🤖 Enviando mensagem para IA...');
    
    const response = await api.post("/api/v1/chat", {
      message,
      timestamp: new Date().toISOString(),
    });

    console.log('✅ Resposta da IA recebida');
    
    return {
      success: true,
      response:
        response.data.reply || response.data.response || response.data.message,
      raw: response.data,
    };
  } catch (error) {
    console.error('❌ Erro no chat com IA:', {
      message: error.message,
      code: error.code,
      response: error.response?.data
    });
    
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
  try {
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
  } catch (error) {
    console.error('❌ Erro na busca inteligente:', error);
    throw error;
  }
};

// =====================================================
// FOLLOWUPS VIA IA
// =====================================================

export const createFollowupViaAI = async (data) => {
  try {
    const response = await api.post("/api/followups/", data);
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('❌ Erro ao criar followup:', error);
    throw error;
  }
};

// =====================================================
// BULLET JOURNAL EXECUTIVO
// =====================================================

// 📘 Bullet Journal é apenas um MODO do chat.
export async function captureExecutive(input) {
  try {
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
  } catch (error) {
    console.error('❌ Erro no bullet journal:', error);
    throw error;
  }
}

// =====================================================
// 📘 HISTÓRICO DO BULLET JOURNAL
// =====================================================

export const getExecutiveJournals = async () => {
  try {
    const response = await api.get("/api/executive-journals");
    return response.data;
  } catch (error) {
    console.error('❌ Erro ao buscar journals:', error);
    throw error;
  }
};

// =====================================================
// 🔥 GLOBAL DEBUG - APENAS EM DESENVOLVIMENTO
// =====================================================

// Expoe globalmente para debug (remove em produção)
if (typeof window !== 'undefined' && 
    (process.env.NODE_ENV === 'development' || 
     (import.meta && import.meta.env && import.meta.env.DEV))) {
  
  window.MAWDSLEYS_API = {
    instance: api,
    baseURL: baseURL,
    testConnection: testBackendConnection,
    getConfig: () => ({
      baseURL: api.defaults.baseURL,
      timeout: api.defaults.timeout,
      headers: api.defaults.headers,
    })
  };
  
  console.log('🔧 MAWDSLEYS API disponível globalmente como window.MAWDSLEYS_API');
  console.log('🌐 BaseURL:', baseURL);
  
  // Teste automático da conexão
  setTimeout(() => {
    testBackendConnection().then(result => {
      console.log('🧪 Teste automático de conexão:', result.connected ? '✅ CONECTADO' : '❌ FALHOU');
    });
  }, 1000);
}

// =====================================================
// EXPORT DEFAULT
// =====================================================

export default api;
// ✅ FIX COMPLETO: 2026-02-06