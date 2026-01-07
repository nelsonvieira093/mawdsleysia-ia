// frontend/src/pages/Login.jsx
import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate, Link } from "react-router-dom";

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

      <style jsx>{`
        .auth-wrapper {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: #0a0a0a;
          background-image: 
            radial-gradient(circle at 15% 50%, rgba(33,33,33,0.3) 0%, transparent 55%),
            radial-gradient(circle at 85% 30%, rgba(33,33,33,0.2) 0%, transparent 55%);
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        }
        
        .auth-card {
          background: #121212;
          border-radius: 8px;
          border: 1px solid #333;
          box-shadow: 0 10px 40px rgba(0,0,0,0.5);
          padding: 40px;
          width: 100%;
          max-width: 480px;
        }
        
        .header-section {
          text-align: center;
          margin-bottom: 30px;
          border-bottom: 1px solid #333;
          padding-bottom: 20px;
        }
        
        .header-section h1 {
          color: #fff;
          margin: 0 0 10px 0;
          font-size: 24px;
          font-weight: 700;
          letter-spacing: 1px;
        }
        
        .header-section h2 {
          color: #ccc;
          margin: 0;
          font-size: 18px;
          font-weight: 400;
        }
        
        .backend-status {
          padding: 12px;
          border-radius: 6px;
          margin-bottom: 25px;
          text-align: center;
          font-size: 14px;
          font-weight: 500;
        }
        
        .backend-status.connected {
          background-color: rgba(76, 175, 80, 0.1);
          color: #4CAF50;
          border: 1px solid rgba(76, 175, 80, 0.3);
        }
        
        .backend-status.disconnected {
          background-color: rgba(255, 193, 7, 0.1);
          color: #FFC107;
          border: 1px solid rgba(255, 193, 7, 0.3);
        }
        
        .auth-form {
          display: flex;
          flex-direction: column;
          gap: 25px;
        }
        
        .form-group {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        label {
          font-weight: 500;
          color: #bbb;
          font-size: 14px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .input, select {
          padding: 14px 16px;
          background: #1a1a1a;
          border: 1px solid #333;
          border-radius: 6px;
          font-size: 15px;
          color: #fff;
          transition: all 0.3s ease;
        }
        
        .input:focus, select:focus {
          outline: none;
          border-color: #666;
          box-shadow: 0 0 0 2px rgba(102, 102, 102, 0.1);
        }
        
        .input:read-only {
          background-color: #222;
          color: #888;
          cursor: not-allowed;
        }
        
        select {
          appearance: none;
          background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%23888' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14L2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
          background-repeat: no-repeat;
          background-position: right 16px center;
          background-size: 16px;
          padding-right: 40px;
        }
        
        .hint-text {
          color: #666;
          font-size: 12px;
          margin-top: 4px;
          font-style: italic;
        }
        
        .btn {
          background: #222;
          color: #fff;
          border: 1px solid #444;
          padding: 16px;
          border-radius: 6px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          text-transform: uppercase;
          letter-spacing: 1px;
          margin-top: 10px;
        }
        
        .btn:hover {
          background: #333;
          border-color: #555;
        }
        
        .btn:active {
          background: #2a2a2a;
          transform: translateY(1px);
        }
        
        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          background: #222;
        }
        
        .spinner {
          display: inline-block;
          width: 18px;
          height: 18px;
          border: 2px solid #fff;
          border-top-color: transparent;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
          margin-right: 8px;
        }
        
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        
        .alert-error {
          background-color: rgba(244, 67, 54, 0.1);
          border: 1px solid rgba(244, 67, 54, 0.3);
          color: #f44336;
          padding: 14px;
          border-radius: 6px;
          margin-bottom: 20px;
          font-size: 14px;
          display: flex;
          align-items: center;
          gap: 10px;
        }
        
        .system-info {
          margin-top: 25px;
          padding: 20px;
          background-color: #1a1a1a;
          border-radius: 6px;
          font-size: 14px;
          color: #888;
          border: 1px solid #333;
        }
        
        .system-info p {
          margin: 0 0 10px 0;
        }
        
        .system-info p:last-child {
          margin-bottom: 0;
        }
        
        .system-info strong {
          color: #bbb;
        }
        
        .docs-link {
          color: #4a9eff;
          text-decoration: none;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          font-weight: 500;
          transition: color 0.3s;
        }
        
        .docs-link:hover {
          color: #6ab1ff;
          text-decoration: underline;
        }
        
        .credentials-section {
          margin-top: 20px;
          padding: 20px;
          background-color: #1a1a1a;
          border-radius: 6px;
          border: 1px solid #333;
        }
        
        .section-title {
          color: #bbb;
          font-weight: 600;
          margin: 0 0 15px 0;
          font-size: 14px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .credential-item {
          margin-bottom: 12px;
          padding-bottom: 12px;
          border-bottom: 1px solid #2a2a2a;
        }
        
        .credential-item:last-child {
          margin-bottom: 0;
          padding-bottom: 0;
          border-bottom: none;
        }
        
        .credential-name {
          display: block;
          color: #fff;
          font-weight: 500;
          margin-bottom: 4px;
          font-size: 14px;
        }
        
        .credential-details {
          display: block;
          color: #888;
          font-size: 13px;
          font-family: 'Courier New', monospace;
        }
        
        /* Responsividade */
        @media (max-width: 600px) {
          .auth-card {
            padding: 30px 20px;
          }
          
          .header-section h1 {
            font-size: 20px;
          }
          
          .header-section h2 {
            font-size: 16px;
          }
          
          .input, select {
            padding: 12px 14px;
          }
          
          .btn {
            padding: 14px;
          }
        }
      `}</style>
    </div>
  );
}