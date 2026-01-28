// frontend/src/pages/ExecutiveJournalHistory.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import ExecutiveBlock from "../components/ExecutiveBlock";
import { getExecutiveJournals } from "../services/api";

import "./ExecutiveJournalHistory.css"; // ✅ CSS correto

export default function ExecutiveJournalHistory() {
  const [journals, setJournals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    try {
      const data = await getExecutiveJournals();
      setJournals(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Erro ao carregar histórico executivo", err);
      setJournals([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="executive-history-container">
      <Sidebar />

      <div className="executive-history-main">
        {/* HEADER */}
        <div className="executive-history-header">
          <div>
            <h1 className="executive-history-title">
              📘 Histórico do Bullet Journal
            </h1>
            <p className="executive-history-subtitle">
              Registros executivos estruturados salvos no sistema
            </p>
          </div>
        </div>

        {/* CONTEÚDO */}
        {loading && (
          <div className="history-loading">Carregando registros...</div>
        )}

        {!loading && journals.length === 0 && (
          <div className="history-empty">
            Nenhum registro executivo encontrado.
          </div>
        )}

        {!loading && journals.length > 0 && (
          <div className="journal-list">
            {journals.map((j) => (
              <div key={j.id} className="journal-card">
                <div className="journal-card-header">
                  <span className="journal-date">
                    {new Date(j.created_at).toLocaleString("pt-BR")}
                  </span>

                  <span className="journal-mode">{j.mode || "CEO"}</span>
                </div>

                {/* BLOCO EXECUTIVO REUTILIZADO (NÃO QUEBRADO) */}
                <ExecutiveBlock data={j} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
