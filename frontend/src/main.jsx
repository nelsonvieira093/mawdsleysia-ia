// E:\MAWDSLEYS-AGENTE\frontend\src\main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { AIProvider } from "./contexts/AIContext";
import RouterApp from "./Router";
import "./index.css";

// =====================================================
// 🔥 CARREGAMENTO DA API - ADICIONE ESTA PARTE
// =====================================================

// Função para carregar e configurar a API
const initializeAPI = async () => {
  try {
    // Importa dinamicamente o serviço de API
    const apiModule = await import("./services/api.js");

    console.log("🚀 API Service carregado");

    // Expoe funções principais globalmente
    window.MAWDSLEYS_API = {
      // Instância axios principal
      axios: apiModule.default,

      // URL base (importante para debug)
      baseURL: apiModule.baseURL,

      // Funções principais que o app precisa
      testConnection: apiModule.testBackendConnection,
      adminLogin: apiModule.adminLogin,
      chatWithAI: apiModule.chatWithAI,
      getAIContext: apiModule.getAIContext,
      smartSearch: apiModule.smartSearch,
      checkWeeklyMeetings: apiModule.checkWeeklyMeetings,
      getExecutiveJournals: apiModule.getExecutiveJournals,

      // Helper para debug
      getConfig: () => ({
        baseURL: apiModule.default.defaults.baseURL,
        timeout: apiModule.default.defaults.timeout,
        headers: apiModule.default.defaults.headers,
      }),
    };

    // Teste automático de conexão
    const connectionTest = await apiModule.testBackendConnection();
    if (connectionTest.connected) {
      console.log("✅ Backend conectado:", apiModule.baseURL);
    } else {
      console.warn("⚠️ Backend pode estar offline:", connectionTest.error);
    }

    return true;
  } catch (error) {
    console.error("❌ Falha ao carregar API service:", error);

    // Fallback: API básica com fetch
    window.MAWDSLEYS_API = {
      baseURL: "https://backend-silent-snowflake-7300.fly.dev",

      async request(endpoint, options = {}) {
        const url = endpoint.startsWith("http")
          ? endpoint
          : this.baseURL + endpoint;

        const response = await fetch(url, {
          ...options,
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            ...options.headers,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        return response.json();
      },

      get(endpoint) {
        return this.request(endpoint);
      },

      post(endpoint, data) {
        return this.request(endpoint, {
          method: "POST",
          body: JSON.stringify(data),
        });
      },

      testConnection: async () => {
        try {
          const response = await fetch(`${this.baseURL}/health`);
          return {
            connected: response.ok,
            status: response.status,
            url: this.baseURL,
          };
        } catch (error) {
          return { connected: false, error: error.message };
        }
      },
    };

    console.log("⚠️ Usando API fallback (fetch)");
    return false;
  }
};

// =====================================================
// INICIALIZAÇÃO DA APLICAÇÃO
// =====================================================

// Primeiro inicializa a API, depois renderiza o React
initializeAPI()
  .then((apiLoaded) => {
    console.log(apiLoaded ? "✅ API pronta" : "⚠️ API em modo fallback");

    // Agora renderiza a aplicação React
    ReactDOM.createRoot(document.getElementById("root")).render(
      <React.StrictMode>
        <AuthProvider>
          <BrowserRouter>
            <AIProvider>
              <RouterApp />
            </AIProvider>
          </BrowserRouter>
        </AuthProvider>
      </React.StrictMode>,
    );
  })
  .catch((error) => {
    console.error("❌ Erro crítico na inicialização:", error);

    // Renderiza mesmo com erro, mas mostra aviso
    ReactDOM.createRoot(document.getElementById("root")).render(
      <React.StrictMode>
        <div style={{ padding: "20px", color: "red" }}>
          <h1>⚠️ Erro na inicialização do sistema</h1>
          <p>
            Por favor, recarregue a página. Se o problema persistir, entre em
            contato com o suporte.
          </p>
          <p>Erro técnico: {error.message}</p>
        </div>
      </React.StrictMode>,
    );
  });
