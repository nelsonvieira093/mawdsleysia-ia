// frontend/src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";
import "./Dashboard.css";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

function KpiCard({ title, value, trend }) {
  return (
    <div className="kpi-card">
      <div className="kpi-top">
        <div className="kpi-title">{title}</div>
        <div className={`kpi-trend ${trend}`}>
          {trend === "up" ? "⬆" : trend === "down" ? "⬇" : "•"}
        </div>
      </div>
      <div className="kpi-value">{value}</div>
    </div>
  );
}

export default function Dashboard() {
  const [kpis, setKpis] = useState([]);
  const [followups, setFollowups] = useState([]);
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);

  // =========================
  // FALLBACK DATA (DEMO SAFE)
  // =========================
  const fallbackKpis = [
    { area: "Financeiro", value: "Margem 38%", trend: "up" },
    { area: "Operações", value: "OTIF 92%", trend: "down" },
    { area: "Comercial", value: "Forecast +4%", trend: "up" },
    { area: "Regulatório", value: "12 RFIs pendentes", trend: "alert" },
  ];

  const lineDataFallback = [
    { month: "Ago", revenue: 120, forecast: 100 },
    { month: "Set", revenue: 150, forecast: 140 },
    { month: "Out", revenue: 170, forecast: 160 },
    { month: "Nov", revenue: 180, forecast: 190 },
    { month: "Dez", revenue: 220, forecast: 210 },
  ];

  const barDataFallback = [
    { name: "OTIF", value: 92 },
    { name: "Devol.", value: 4 },
    { name: "Atrasos", value: 8 },
    { name: "Stockouts", value: 3 },
  ];

  const pieDataFallback = [
    { name: "RFIs Abertos", value: 12 },
    { name: "RFIs Concluídos", value: 28 },
    { name: "RFIs Em Análise", value: 8 },
  ];

  const colors = ["#4b7cff", "#7bed8d", "#ffd166", "#ff6b6b"];

  useEffect(() => {
    loadDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadDashboard() {
    setLoading(true);
    try {
      const [kpiRes, fuRes, meetRes] = await Promise.allSettled([
        api.get("api/kpis"),
        api.get("api/agenda/followups"),
        api.get("api/meetings"),
      ]);

      // KPIs
      if (kpiRes.status === "fulfilled" && Array.isArray(kpiRes.value.data)) {
        setKpis(kpiRes.value.data);
      } else {
        setKpis(fallbackKpis);
      }

      // Followups
      if (fuRes.status === "fulfilled" && Array.isArray(fuRes.value.data)) {
        setFollowups(fuRes.value.data.slice(0, 6));
      } else {
        setFollowups([
          {
            id: 1,
            title: "Enviar Forecast BD",
            owner: "Gabriel",
            priority: "Alta",
            deadline: "Hoje",
          },
          {
            id: 2,
            title: "Revisar SNOP",
            owner: "Éder",
            priority: "Média",
            deadline: "Amanhã",
          },
        ]);
      }

      // Meetings
      if (meetRes.status === "fulfilled" && Array.isArray(meetRes.value.data)) {
        setMeetings(meetRes.value.data.slice(0, 5));
      } else {
        setMeetings([
          { id: 1, title: "SNOP", date: "2025-12-08 10:00", owner: "Éder" },
          {
            id: 2,
            title: "One-on-One",
            date: "2025-12-08 15:00",
            owner: "Luiz",
          },
        ]);
      }
    } catch (err) {
      console.error("Erro ao carregar dashboard:", err);
      setKpis(fallbackKpis);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="dashboard-container">
      <Sidebar />

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <h1 className="dashboard-title">Painel Executivo — MAWDSLEYS</h1>
            <p className="dashboard-sub">
              Visão unificada: KPIs, Pautas e Follow-ups
            </p>
          </div>

          <div className="header-actions">
            <button className="btn small" onClick={loadDashboard}>
              ⟳ Atualizar
            </button>
            <button className="btn outline small">Exportar PDF</button>
          </div>
        </header>

        <section className="kpi-row">
          {kpis.map((k, idx) => (
            <KpiCard
              key={idx}
              title={k.area}
              value={k.value}
              trend={k.trend || (idx % 2 ? "down" : "up")}
            />
          ))}
        </section>

        <section className="visual-row">
          <div className="visual-left card">
            <h3>Forecast Comercial</h3>
            <div style={{ height: 220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={lineDataFallback}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line dataKey="revenue" stroke="#4b7cff" strokeWidth={3} />
                  <Line dataKey="forecast" stroke="#7bed8d" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="visual-right">
            <div className="card small-card">
              <h4>KPIs Operacionais</h4>
              <div style={{ height: 160 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barDataFallback}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#ffd166" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card small-card">
              <h4>RFIs (Regulatório)</h4>
              <div style={{ height: 140 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieDataFallback}
                      dataKey="value"
                      outerRadius={50}
                    >
                      {pieDataFallback.map((_, i) => (
                        <Cell key={i} fill={colors[i % colors.length]} />
                      ))}
                    </Pie>
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
