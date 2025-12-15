// E:\MAWDSLEYS-AGENTE\frontend\src\contexts\AuthContext.jsx
import { createContext, useContext, useState, useEffect } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ==============================
  // RESTAURA SESSÃO AO CARREGAR
  // ==============================
  useEffect(() => {
    const token = localStorage.getItem("token");
    const userRaw = localStorage.getItem("user");

    if (token && userRaw) {
      try {
        const parsedUser = JSON.parse(userRaw);
        api.defaults.headers.common.Authorization = `Bearer ${token}`;
        setUser(parsedUser);
      } catch {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }

    setLoading(false);
  }, []);

  // ==============================
  // LOGIN CORRIGIDO - Compatível com backend REAL
  // ==============================
  async function login(email, password) {
    try {
      console.log("🔐 Tentando login com:", { email });

      const res = await api.post("/auth/login", {
        email,
        password,
      });

      console.log("✅ Resposta do backend:", res.data);

      // 🔥 CORREÇÃO AQUI: O backend retorna { access_token, user_id, email }
      // Não retorna um objeto "user" completo
      const {
        access_token,
        token, // algumas APIs usam "token" em vez de "access_token"
        user_id,
        email: userEmail,
        name = "Usuário",
        role = "user",
      } = res.data;

      // Usar o token disponível
      const actualToken = access_token || token;

      if (!actualToken) {
        console.error("❌ Token não encontrado na resposta:", res.data);
        throw new Error("Token não recebido do servidor");
      }

      // Criar objeto user manualmente
      const user = {
        id: user_id || Date.now(), // fallback se não tiver ID
        email: userEmail || email,
        name: res.data.name || name,
        role: role,
      };

      console.log("👤 Usuário criado:", user);

      localStorage.setItem("token", actualToken);
      localStorage.setItem("user", JSON.stringify(user));

      api.defaults.headers.common.Authorization = `Bearer ${actualToken}`;
      setUser(user);

      return true;
    } catch (err) {
      console.error("❌ ERRO NO LOGIN:");
      console.error("  Status:", err.response?.status);
      console.error("  Data:", err.response?.data);
      console.error("  Mensagem:", err.message);

      // Mensagem amigável para o usuário
      if (err.response?.status === 404) {
        throw new Error(
          "Servidor não encontrado. Verifique se o backend está rodando."
        );
      } else if (err.response?.status === 401) {
        throw new Error("Credenciais inválidas");
      } else {
        throw new Error("Erro de conexão com o servidor");
      }
    }
  }

  // ==============================
  // SIGNUP CORRIGIDO
  // ==============================
  async function signup({ name, email, password }) {
    try {
      console.log("📝 Tentando cadastro:", { name, email });

      const res = await api.post("/auth/signup", {
        name,
        email,
        password,
      });

      console.log("✅ Resposta do signup:", res.data);

      // Após cadastro, fazer login automaticamente
      return await login(email, password);
    } catch (err) {
      console.error("❌ Erro no cadastro:");
      console.error("  Status:", err.response?.status);
      console.error("  Data:", err.response?.data);

      if (err.response?.status === 409) {
        throw new Error("Email já cadastrado");
      } else {
        throw new Error("Erro ao criar conta. Tente novamente.");
      }
    }
  }

  // ==============================
  // LOGOUT
  // ==============================
  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    delete api.defaults.headers.common.Authorization;
    setUser(null);
  }

  // ==============================
  // VERIFICAR TOKEN (nova função)
  // ==============================
  async function verifyToken() {
    try {
      const token = localStorage.getItem("token");
      if (!token) return false;

      // Tentar endpoint /me ou similar
      const res = await api.get("/auth/me");
      if (res.data) {
        setUser(res.data);
        return true;
      }
      return false;
    } catch {
      logout();
      return false;
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        signup,
        logout,
        verifyToken,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);

  if (!ctx) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }

  return ctx;
}
