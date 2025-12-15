// E:\MAWDSLEYS-AGENTE\frontend\src\pages\Login.jsx
import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();

  const [email, setEmail] = useState("nelsonronnyr40@gmail.com");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function send(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const ok = await login(email, password);

      if (ok) {
        nav("/dashboard");
      }
    } catch (err) {
      setError(
        err.message || "Credenciais inválidas ou servidor indisponível."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h2>Entrar no MAWDSLEYS</h2>

        {error && <div className="alert alert-error">❌ {error}</div>}

        <form onSubmit={send} className="auth-form">
          <input
            className="input"
            placeholder="E-mail"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
          />

          <input
            className="input"
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
          />

          <button className="btn" type="submit" disabled={loading}>
            {loading ? "Conectando..." : "Entrar"}
          </button>

          <div style={{ marginTop: 20, fontSize: 14, color: "#666" }}>
            <p>
              <strong>Dica:</strong> O backend deve estar rodando em:
            </p>
            <p>http://localhost:8000</p>
            <p>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
              >
                📚 Ver documentação da API
              </a>
            </p>
          </div>

          <p className="auth-footer">
            Não tem conta? <Link to="/signup">Criar</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
