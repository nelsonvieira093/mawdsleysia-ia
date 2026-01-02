import { createContext, useContext, useState, useEffect } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ==============================
  // RESTAURA SESSÃO
  // ==============================
  useEffect(() => {
    const token = localStorage.getItem("token");
    const userRaw = localStorage.getItem("user");

    if (token && userRaw) {
      try {
        api.defaults.headers.common.Authorization = `Bearer ${token}`;
        setUser(JSON.parse(userRaw));
      } catch {
        localStorage.clear();
      }
    }

    setLoading(false);
  }, []);

  // ==============================
  // LOGIN ADMIN FIXO
  // ==============================
  async function login(email, password) {
    try {
      const res = await api.post("/admin-login", { email, password });

      const { access_token, user } = res.data;

      if (!access_token || !user) {
        throw new Error("Resposta inválida do servidor");
      }

      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(user));

      api.defaults.headers.common.Authorization = `Bearer ${access_token}`;
      setUser(user);

      return true;
    } catch (err) {
      if (err.response?.status === 401) {
        throw new Error("Credenciais inválidas");
      }
      throw new Error("Erro de conexão com o servidor");
    }
  }

  // ==============================
  // LOGOUT
  // ==============================
  function logout() {
    localStorage.clear();
    delete api.defaults.headers.common.Authorization;
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth fora do AuthProvider");
  return ctx;
}
