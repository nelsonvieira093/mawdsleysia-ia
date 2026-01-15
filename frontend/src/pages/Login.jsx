// frontend/src/pages/Login.jsx
import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import "./Login.css";


export default function Login() {
  const { login, backendConnected } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("nelsonronnyr40@gmail.com");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Preenche senha baseada no email selecionado
  useEffect(() => {
    if (email === "nelsonronnyr40@gmail.com") {
      setPassword("Admin@2024");
    } else if (email === "danielac@mbbpharma.com.br") {
      setPassword("Daniela@123");
    } else {
      setPassword("");
    }
  }, [email]);

  async function send(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const ok = await login(email, password);

      if (ok) {
        navigate("/dashboard");
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
        <div className="header-section">
          <h1>MAWDSLEYS</h1>
          <h2>Login Administrativo</h2>
        </div>

        {error && <div className="alert alert-error">❌ {error}</div>}

        {/* Status do backend */}
        <div className={`backend-status ${backendConnected ? 'connected' : 'disconnected'}`}>
          {backendConnected ? (
            <span>✅ Conectado ao servidor</span>
          ) : (
            <span>⚠️ Aguardando conexão com servidor...</span>
          )}
        </div>

        <form onSubmit={send} className="auth-form">
          <div className="form-group">
            <label>E-mail:</label>
            <select 
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            >
              <option value="nelsonronnyr40@gmail.com">Nelson Vieira (Super Admin)</option>
              <option value="danielac@mbbpharma.com.br">Daniela M. Carraro (Admin)</option>
            </select>
            <small className="hint-text">
              Será preenchida automaticamente para o administrador selecionado
            </small>
          </div>

          <div className="form-group">
            <label>Senha:</label>
            <input
              className="input"
              type="password"
              placeholder="Senha"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              readOnly
            />
          </div>

          <button className="btn" type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span> Conectando...
              </>
            ) : (
              "Entrar"
            )}
          </button>

          <div className="system-info">
            <p><strong>Sistema de Administração</strong></p>
            <p>
              <strong>Backend:</strong> backend-silent-snowflake-7300.fly.dev
            </p>
            <p>
              <a
                href="https://backend-silent-snowflake-7300.fly.dev/docs"
                target="_blank"
                rel="noreferrer"
                className="docs-link"
              >
                📚 Ver documentação da API
              </a>
            </p>
          </div>

          <div className="credentials-section">
            <p className="section-title">Credenciais de Administrador:</p>
            <div className="credential-item">
              <span className="credential-name">Nelson Vieira:</span>
              <span className="credential-details">nelsonronnyr40@gmail.com / Admin@2024</span>
            </div>
            <div className="credential-item">
              <span className="credential-name">Daniela M. Carraro:</span>
              <span className="credential-details">danielac@mbbpharma.com.br / Daniela@123</span>
            </div>
          </div>
        </form>
      </div>

      
    </div>
  );
}