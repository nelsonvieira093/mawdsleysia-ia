// frontend/src/contexts/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ⚠️ backend começa como ONLINE por padrão
  const [backendConnected, setBackendConnected] = useState(true);

  // ==============================
  // HEALTH CHECK (NÃO BLOQUEANTE)
  // ==============================
  useEffect(() => {
    let mounted = true;

    const checkBackend = async () => {
      try {
        console.log("🔗 Verificando saúde do backend...");

        // tentativa leve, sem impacto no app
        await api.get("/health", { timeout: 8000 });

        if (!mounted) return;

        setBackendConnected(true);
        console.log("🔗 Backend health: ✅ OK");
      } catch (err) {
        if (!mounted) return;

        // ⚠️ timeout NÃO derruba sistema
        console.warn("⚠️ Health check demorou, mas app continua:", err.message);

        // mantém estado como true
        setBackendConnected(true);
      }
    };

    checkBackend();

    return () => {
      mounted = false;
    };
  }, []);

  // ==============================
  // RESTAURA SESSÃO
  // ==============================
  useEffect(() => {
    const token = localStorage.getItem("token");
    const userRaw = localStorage.getItem("user");

    if (token && userRaw) {
      try {
        const parsedUser = JSON.parse(userRaw);
        setUser(parsedUser);
        console.log("👤 Sessão restaurada:", parsedUser.name);
      } catch {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }

    setLoading(false);
  }, []);

  // ==============================
  // LOGIN
  // ==============================
  async function login(email, password) {
    try {
      console.log("🔐 Tentando login:", email);

      const response = await api.post("/api/v1/auth/admin-login", {
        email,
        password,
      });

      const tokenData = response.data;
      const access_token = tokenData.access_token || tokenData.token;

      if (!access_token) {
        throw new Error("Token não retornado");
      }

      const user = tokenData.user;

      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(user));

      api.defaults.headers.common.Authorization = `Bearer ${access_token}`;

      setUser(user);
      setBackendConnected(true);

      console.log("✅ Login realizado:", user.name);
      return true;
    } catch (err) {
      console.error("❌ Erro no login:", err.message);

      if (err.response?.status === 401) {
        throw new Error("Email ou senha incorretos.");
      }

      throw new Error("Erro ao conectar com o servidor.");
    }
  }

  // ==============================
  // LOGOUT
  // ==============================
  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    console.log("👋 Logout realizado");
    window.location.href = "/login";
  }

  // ==============================
  // AUTORIZAÇÃO
  // ==============================
  function isAdmin() {
    return (
      user?.is_admin === true ||
      user?.role === "admin" ||
      user?.role === "super_admin"
    );
  }

  function isSuperAdmin() {
    return user?.email === "nelsonronnyr40@gmail.com";
  }

  const isAuthenticated = !!user;

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        login,
        logout,
        loading,
        isAdmin,
        isSuperAdmin,
        backendConnected, // agora é informativo
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
