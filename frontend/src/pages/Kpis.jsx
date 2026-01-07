// frontend/src/pages/Kpis.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";
import "./Kpis.css";

function SummaryCard({ label, value }) {
  return (
    <div className="summary-card">
      <span className="summary-label">{label}</span>
      <strong className="summary-value">{value}</strong>
    </div>
  );
}

function KpiCard({ area, value, trend, description, impact, action }) {
  return (
    <div className={`kpi-card ${trend}`}>
      <div className="kpi-header">
        <h3>{area}</h3>
        <span className="kpi-trend">
          {trend === "up" && "⬆ Positivo"}
          {trend === "down" && "⬇ Negativo"}
          {trend === "alert" && "⚠️ Atenção"}
        </span>
      </div>

      <div className="kpi-value">{value}</div>

      <p className="kpi-description">{description}</p>

      <div className="kpi-meta">
        <div>
          <strong>Impacto:</strong>
          <span>{impact}</span>
        </div>
        <div>
          <strong>Ação recomendada:</strong>
          <span>{action}</span>
        </div>
      </div>
    </div>
  );
}

export default function Kpis() {
  const [kpis, setKpis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  // 🔒 FALLBACK EXECUTIVO COMPLETO
  const fallbackKpis = [
    {
      area: "Financeiro",
      value: "Margem 38%",
      trend: "up",
      description: "Margem operacional acima do target trimestral.",
      impact: "Aumento da rentabilidade e maior capacidade de investimento.",
      action: "Manter política de custos e revisar oportunidades de expansão.",
    },
    {
      area: "Operações",
      value: "OTIF 92%",
      trend: "down",
      description: "Redução pontual no índice de entregas no prazo.",
      impact: "Risco de insatisfação de clientes estratégicos.",
      action: "Revisar cadeia logística e níveis de estoque.",
    },
    {
      area: "Comercial",
      value: "Forecast +4%",
      trend: "up",
      description: "Previsão de vendas acima do orçamento aprovado.",
      impact: "Maior geração de caixa no curto prazo.",
      action: "Ajustar capacidade operacional para absorver demanda.",
    },
    {
      area: "Regulatório",
      value: "12 RFIs em aberto",
      trend: "alert",
      description: "Demandas regulatórias aguardando resposta.",
      impact: "Risco de penalidades ou atrasos em liberações.",
      action: "Priorizar respostas com apoio jurídico e técnico.",
    },
    {
      area: "Pessoas",
      value: "Turnover 6%",
      trend: "up",
      description: "Redução do turnover em relação ao mês anterior.",
      impact: "Retenção de conhecimento e estabilidade operacional.",
      action: "Reforçar políticas de engajamento e desenvolvimento.",
    },
  ];

  useEffect(() => {
    loadKpis();
  }, []);

  const loadKpis = async () => {
    try {
      const res = await api.get("/api/kpis");

      if (Array.isArray(res.data) && res.data.length > 0) {
        setKpis(res.data);
      } else {
        setKpis(fallbackKpis);
      }
    } catch {
      setKpis(fallbackKpis);
    } finally {
      setLastUpdate(new Date().toLocaleString("pt-BR"));
      setLoading(false);
    }
  };

  const total = kpis.length;
  const positive = kpis.filter((k) => k.trend === "up").length;
  const alerts = kpis.filter((k) => k.trend !== "up").length;

  return (
    <div className="kpis-page">
      <Sidebar />

      <main className="kpis-main">
        <header className="kpis-header">
          <h1>KPIs Estratégicos</h1>
          <p>
            Indicadores consolidados automaticamente pelo Agente MAWDSLEYS para
            suporte à tomada de decisão executiva.
          </p>
        </header>

        {/* RESUMO EXECUTIVO */}
        <section className="kpis-summary">
          <SummaryCard label="Áreas monitoradas" value={total} />
          <SummaryCard label="Indicadores positivos" value={positive} />
          <SummaryCard label="Alertas ativos" value={alerts} />
          <SummaryCard label="Última atualização" value={lastUpdate || "—"} />
        </section>

        {/* CONTEÚDO */}
        {loading ? (
          <div className="loading">
            <h3>Processando indicadores estratégicos…</h3>
            <p>
              O Agente MAWDSLEYS está consolidando dados financeiros,
              operacionais, comerciais e regulatórios.
            </p>
          </div>
        ) : (
          <section className="kpis-grid">
            {kpis.map((kpi, index) => (
              <KpiCard key={index} {...kpi} />
            ))}
          </section>
        )}
      </main>
    </div>
  );
}
