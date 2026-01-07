// frontend/src/contexts/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from "react";
import { adminLogin, testBackendConnection } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [backendConnected, setBackendConnected] = useState(false);

  // ==============================
  // TESTA CONEXÃO COM BACKEND
  // ==============================
  useEffect(() => {
    const checkBackend = async () => {
      const result = await testBackendConnection();
      setBackendConnected(result.connected);
      console.log(
        "🔗 Backend connection:",
        result.connected ? "✅ OK" : "❌ FAILED"
      );
    };
    checkBackend();
  }, []);

  // ==============================
  // RESTAURA SESSÃO AO CARREGAR
  // ==============================
  useEffect(() => {
    const token = localStorage.getItem("token");
    const userRaw = localStorage.getItem("user");

    if (token && userRaw) {
      try {
        const parsedUser = JSON.parse(userRaw);
        // Não precisa configurar header aqui, pois o interceptor do axios faz isso
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
  // LOGIN COM ADMIN FIXO
  // ==============================
  async function login(email, password) {
    try {
      console.log("🔐 Tentando login:", { email });

      // Verifica se backend está conectado
      if (!backendConnected) {
        const result = await testBackendConnection();
        setBackendConnected(result.connected);

        if (!result.connected) {
          throw new Error(
            "Servidor não está respondendo. Verifique a conexão."
          );
        }
      }

      // ADMIN FIXO: Usa apenas o endpoint admin-login
      const result = await adminLogin(email, password);

      if (result.success) {
        setUser(result.user);
        console.log("✅ Login bem-sucedido:", result.user.name);
        return true;
      } else {
        throw new Error(result.error || "Credenciais inválidas");
      }
    } catch (err) {
      console.error("❌ ERRO NO LOGIN:", err.message);

      // Mensagens amigáveis
      if (err.message.includes("Servidor não está respondendo")) {
        throw new Error(
          "Backend não disponível. Tente novamente em alguns instantes."
        );
      } else if (err.message.includes("Credenciais inválidas")) {
        throw new Error("Email ou senha incorretos.");
      } else {
        throw new Error("Erro ao conectar com o servidor.");
      }
    }
  }

  // ==============================
  // SIGNUP (DESABILITADO - APENAS ADMINS FIXOS)
  // ==============================
  async function signup({ name, email, password }) {
    // Não permite cadastro, apenas admins fixos
    throw new Error("Cadastro desabilitado. Use as contas de administrador.");
  }

  // ==============================
  // LOGOUT
  // ==============================
  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    console.log("👋 Usuário deslogado");
  }

  // ==============================
  // VERIFICAR TOKEN
  // ==============================
  async function verifyToken() {
    try {
      const token = localStorage.getItem("token");
      if (!token) return false;

      // Verifica se token é válido checando user no localStorage
      const userRaw = localStorage.getItem("user");
      if (userRaw) {
        const user = JSON.parse(userRaw);
        setUser(user);
        return true;
      }
      return false;
    } catch {
      logout();
      return false;
    }
  }

  // ==============================
  // VERIFICAR SE É ADMIN
  // ==============================
  function isAdmin() {
    return (
      user?.is_admin === true ||
      user?.role === "admin" ||
      user?.role === "super_admin"
    );
  }

  // ==============================
  // VERIFICAR SE É NELSON (SUPER ADMIN)
  // ==============================
  function isSuperAdmin() {
    return user?.email === "nelsonronnyr40@gmail.com";
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
        isAdmin,
        isSuperAdmin,
        backendConnected,
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
