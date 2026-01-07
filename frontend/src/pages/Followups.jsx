// frontend/src/pages/Followups.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";
import "./Followups.css";

function FollowupCard({ item }) {
  return (
    <div className={`followup-card priority-${item.priority?.toLowerCase()}`}>
      <div className="followup-header">
        <h3>{item.title}</h3>
        <span className={`status-badge status-${item.status}`}>
          {item.status?.toUpperCase()}
        </span>
      </div>

      <p className="followup-description">{item.description}</p>

      <div className="followup-meta">
        <span>
          <strong>Responsável:</strong> {item.owner}
        </span>
        <span>
          <strong>Prazo:</strong> {item.deadline}
        </span>
        <span>
          <strong>Área:</strong> {item.area}
        </span>
      </div>

      <div className="followup-actions">
        <button className="btn-view">Ver</button>
        <button className="btn-edit">Editar</button>
      </div>
    </div>
  );
}

export default function Followups() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  // 🔒 FALLBACK EXECUTIVO (DEMO)
  const fallbackFollowups = [
    {
      id: 1,
      title: "Enviar Forecast Atualizado",
      description:
        "Consolidar números do comercial e enviar forecast revisado para diretoria.",
      owner: "Gabriel",
      deadline: "Hoje",
      priority: "Alta",
      status: "aberto",
      area: "Comercial",
    },
    {
      id: 2,
      title: "Responder RFI Anvisa",
      description: "Preparar documentação solicitada pelo órgão regulador.",
      owner: "Daniela",
      deadline: "Amanhã",
      priority: "Alta",
      status: "em-andamento",
      area: "Regulatório",
    },
    {
      id: 3,
      title: "Atualizar SNOP",
      description: "Revisar premissas de demanda e capacidade produtiva.",
      owner: "Éder",
      deadline: "Esta semana",
      priority: "Média",
      status: "aberto",
      area: "Operações",
    },
    {
      id: 4,
      title: "Preparar reunião Board",
      description: "Criar apresentação executiva com KPIs consolidados.",
      owner: "Luiz",
      deadline: "Sexta-feira",
      priority: "Alta",
      status: "pendente",
      area: "Executivo",
    },
  ];

  useEffect(() => {
    loadFollowups();
  }, []);

  const loadFollowups = async () => {
    setLoading(true);
    try {
      const res = await api.get("/api/agenda/followups");

      if (Array.isArray(res.data) && res.data.length > 0) {
        setItems(res.data);
      } else {
        setItems(fallbackFollowups);
      }
    } catch {
      setItems(fallbackFollowups);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="followups-container">
      <Sidebar />

      <main className="followups-main">
        <header className="followups-header">
          <div className="header-left">
            <h1>Follow-ups Estratégicos</h1>
            <p>Ações pendentes monitoradas pelo Agente MAWDSLEYS</p>
          </div>

          <div className="header-actions">
            <button className="btn-refresh" onClick={loadFollowups}>
              ⟳ Atualizar
            </button>
            <button className="btn-primary">+ Novo Follow-up</button>
          </div>
        </header>

        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Carregando follow-ups estratégicos...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📌</div>
            <h3>Nenhum follow-up encontrado</h3>
            <p>Todas as ações estão em dia.</p>
          </div>
        ) : (
          <div className="followups-grid">
            {items.map((item) => (
              <FollowupCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
