// E:\MAWDSLEYS-AGENTE\frontend\src\components\Sidebar.jsx
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./Sidebar.css";
import WhatsAppButton from "./WhatsAppButton";

export default function Sidebar() {
  const { logout } = useAuth();
  const loc = useLocation();

  const menu = [
    {
      group: "Executivo",
      items: [
        { icon: "📊", label: "Dashboard", to: "/" },
        { icon: "📈", label: "KPIs Estratégicos", to: "/kpis" }, // ✅ NOVO
        { icon: "🤖", label: "Chat da IA", to: "/chat" },
        { icon: "🧠", label: "Agente Executivo", to: "/agent" },
      ],
    },
    {
      group: "Rituais & Operações",
      items: [
        { icon: "📅", label: "Pautas da Semana", to: "/agenda" },
        { icon: "📌", label: "Follow-ups", to: "/followups" }, // ✅ NOVO
        { icon: "📁", label: "Entregáveis", to: "/deliverables" },
        { icon: "📜", label: "Histórico", to: "/history" },
      ],
    },
    {
      group: "Base de Conhecimento",
      items: [{ icon: "📚", label: "Documentos", to: "/kb" }],
    },
    {
      group: "Integrações",
      items: [
        /* { icon: "💬", label: "WhatsApp", to: "/whatsapp" }, */
      ],
    },
  ];

  return (
    <div className="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <h2 className="logo">MAWDSLEYS</h2>
        <p className="sub-logo">Agente Executivo</p>
      </div>

      {/* Navegação */}
      <nav className="sidebar-nav">
        {menu.map((section) => (
          <div key={section.group} className="sidebar-section">
            <div className="section-title">{section.group}</div>

            {section.items.map((item) => {
              const isActive = loc.pathname === item.to;

              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`nav-item ${isActive ? "active" : ""}`}
                >
                  <span className="icon">{item.icon}</span>
                  <span className="label">{item.label}</span>
                </Link>
              );
            })}
          </div>
        ))}

        <div className="sidebar-integrations">
          <WhatsAppButton label="WhatsApp" small={false} />
        </div>

        {/* Botão Sair */}
        <button onClick={logout} className="logout-btn">
          🚪 Sair
        </button>
      </nav>
    </div>
  );
}
