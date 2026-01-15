// E:\MAWDSLEYS-AGENTE\frontend\src\components\ProtectedRoute.jsx
import { useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";

export default function ProtectedRoute({ children }) {
  const { loading } = useContext(AuthContext);

  // ⏳ Aguarda inicialização do AuthContext
  if (loading) {
    return null;
  }

  // 🔑 Fonte única da verdade: TOKEN
  const token = localStorage.getItem("token");

  if (!token) {
    window.location.href = "/login";
    return null;
  }

  // ✅ Token existe → libera rota
  return children;
}
