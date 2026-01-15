// E:\MAWDSLEYS-AGENTE\frontend\src\pages\Followups.jsx

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { listFollowups, closeFollowup } from "@/services/followups";
import "./Followups.css";

// ===============================
// Helpers de apresentação
// ===============================
function formatDeadline(dueDate) {
  if (!dueDate) return "—";

  const today = new Date();
  const due = new Date(dueDate);

  const diffDays = Math.ceil(
    (due.setHours(0, 0, 0, 0) - today.setHours(0, 0, 0, 0)) /
      (1000 * 60 * 60 * 24)
  );

  if (diffDays === 0) return "Hoje";
  if (diffDays === 1) return "Amanhã";
  if (diffDays < 0) return "Atrasado";

  return `Em ${diffDays} dias`;
}

function normalizePriority(priority) {
  if (!priority) return "Média";
  return priority.charAt(0).toUpperCase() + priority.slice(1).toLowerCase();
}

function normalizeStatus(status) {
  if (!status) return "aberto";

  const s = status.toLowerCase();

  if (["concluido", "concluído", "closed", "done"].includes(s)) {
    return "concluido";
  }

  return s;
}

// ===============================
// Componente principal
// ===============================
export default function Followups() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);

    try {
      const res = await listFollowups(); // 👈 res DEFINIDO AQUI

      // backend retorna { status, data, count }
      const list = Array.isArray(res.data?.data) ? res.data.data : [];

      const enriched = list.map((f) => ({
        id: f.id,
        title: f.title || "Sem título",
        description: f.description || "",
        owner: f.owner_name || "Responsável não definido",
        deadline: formatDeadline(f.due_date),
        priority: normalizePriority(f.priority),
        status: normalizeStatus(f.status),
        area: f.area || "Geral",
        raw: f,
      }));

      setItems(enriched);
    } catch (err) {
      console.error("Erro ao carregar follow-ups:", err);
      setItems([]);
    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    load();
  }, []);

  const handleClose = async (id) => {
    const confirmed = window.confirm(
      "Tem certeza que deseja marcar este follow-up como concluído?"
    );

    if (!confirmed) return;

    try {
      await closeFollowup(id);
      await load();
    } catch (err) {
      console.error("Erro ao fechar follow-up:", err);
      alert("Não foi possível concluir o follow-up.");
    }
  };

  return (
    <div className="followups-container">
      <Sidebar />

      <main className="followups-main">
        <header className="followups-header">
          <div>
            <h1>Follow-ups Estratégicos</h1>
            <p>Ações pendentes monitoradas pelo Agente MAWDSLEYS</p>
          </div>

          <button onClick={load}>⟳ Atualizar</button>
        </header>

        {loading ? (
          <p>Carregando follow-ups…</p>
        ) : items.length === 0 ? (
          <p>Nenhum follow-up encontrado.</p>
        ) : (
          <div className="followups-grid">
            {items.map((f) => (
              <div
                key={f.id}
                className={`followup-card priority-${f.priority.toLowerCase()}`}
              >
                <div className="followup-header">
                  <h3>{f.title}</h3>
                  <span className={`status-badge status-${f.status}`}>
                    {f.status.toUpperCase()}
                  </span>
                </div>

                <p className="followup-description">{f.description}</p>

                <div className="followup-meta">
                  <span>
                    <strong>Responsável:</strong> {f.owner}
                  </span>
                  <span>
                    <strong>Prazo:</strong> {f.deadline}
                  </span>
                  <span>
                    <strong>Área:</strong> {f.area}
                  </span>
                </div>

                <div className="followup-actions">
                  <button onClick={() => navigate(`/followups/${f.id}`)}>
                    Ver
                  </button>

                  <button onClick={() => navigate(`/followups/${f.id}/edit`)}>
                    Editar
                  </button>

                  {f.status !== "concluido" && (
                    <button onClick={() => handleClose(f.id)}>Fechar</button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
