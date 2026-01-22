// frontend/src/components/ExecutiveBlock.jsx
import React from "react";
import "./ExecutiveBlock.css";

export default function ExecutiveBlock({ data }) {
  if (!data) {
    return (
      <div className="executive-block error">
        ⚠️ Nenhum dado executivo disponível.
      </div>
    );
  }

  const {
    hashtags = [],
    summary,
    structured_summary,
    followups = [],
    rituals = [],
    ritual = [],
    directors = [],
    actions = [],
    register_location,
  } = data;

  const finalSummary = summary || structured_summary || "—";

  const finalRituals = rituals.length ? rituals : ritual;

  return (
    <div className="executive-block">
      {/* HASHTAGS — SEMPRE NO TOPO */}
      <div className="executive-hashtags">
        {hashtags.length > 0 ? (
          hashtags.map((tag) => (
            <span key={tag} className="exec-tag">
              #{tag}
            </span>
          ))
        ) : (
          <span className="exec-tag muted">#Unclassified</span>
        )}
      </div>

      <h4 className="exec-title">🧠 Resumo Estruturado</h4>

      <ul className="exec-list">
        <li>
          <b>Síntese da fala:</b>
          <div>{finalSummary}</div>
        </li>

        <li>
          <b>Follow-ups identificados:</b>
          {followups.length > 0 ? (
            <ul>
              {followups.map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
          ) : (
            <div className="muted">Nenhum follow-up identificado</div>
          )}
        </li>

        <li>
          <b>Rito(s) relacionado(s):</b>{" "}
          {finalRituals.length > 0
            ? finalRituals.join(", ")
            : "Não identificado"}
        </li>

        <li>
          <b>Diretoria(s) envolvida(s):</b>{" "}
          {directors.length > 0 ? directors.join(", ") : "Não identificado"}
        </li>

        <li>
          <b>Ações necessárias:</b>
          {actions.length > 0 ? (
            <ul>
              {actions.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          ) : (
            <div className="muted">Nenhuma ação explícita</div>
          )}
        </li>

        <li>
          <b>Onde deve ser registrado:</b> {register_location || "DailyLog"}
        </li>
      </ul>
    </div>
  );
}
