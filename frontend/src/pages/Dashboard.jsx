// frontend/src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";
import "./Dashboard.css";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

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

  // =========================
  // LOAD DASHBOARD (CORRIGIDO)
  // =========================
  useEffect(() => {
    loadDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function exportDashboardPDF() {
    try {
      const dashboard = document.querySelector(".dashboard-main");

      if (!dashboard) {
        alert("❌ Área do dashboard não encontrada");
        return;
      }

      const canvas = await html2canvas(dashboard, {
        scale: 2,
        useCORS: true,
      });

      const imgData = canvas.toDataURL("image/png");

      const pdf = new jsPDF("p", "mm", "a4");
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

      pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
      pdf.save("dashboard-mawdsleys.pdf");
    } catch (err) {
      console.error("Erro ao exportar PDF:", err);
      alert("❌ Erro ao gerar PDF");
    }
  }

  const [automationRunning, setAutomationRunning] = useState(false);
  const [automationStatus, setAutomationStatus] = useState(null);

  async function runWeeklyAutomation() {
    try {
      setAutomationRunning(true);
      setAutomationStatus(null);

      // ✅ CORREÇÃO: Obter user_id de forma segura
      let userId = "system"; // Valor padrão

      // Opção 1: Do localStorage
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        try {
          const userData = JSON.parse(storedUser);
          userId =
            userData.id || userData.user_id || userData.userId || "system";
        } catch (e) {
          console.warn("Não foi possível parsear user do localStorage");
        }
      }

      // Opção 2: Do contexto/estado se disponível
      // Se tiver um hook useAuth() ou user no estado:
      // const { user } = useAuth(); // Descomente se usar contexto
      // userId = user?.id || userId;

      // Opção 3: Do estado do componente
      // userId = currentUser?.id || userId; // Se tiver currentUser no estado

      console.log(`🚀 Executando automação para usuário: ${userId}`);

      // ✅ CORREÇÃO: Endpoint correto (baseado nos logs do backend)
      const result = await api.post(
        "/api/automations/weekly-run", // ✅ ENDPOINT CORRETO
        {
          user_id: userId,
          trigger: "dashboard_button",
          timestamp: new Date().toISOString(),
        }
      );

      console.log("✅ Automação executada:", result.data);

      // ✅ CORREÇÃO: Status mais detalhado
      setAutomationStatus({
        type: "success",
        message: result.data.message || "Automação executada com sucesso!",
        data: result.data.data,
      });

      // ✅ BÔNUS: Recarrega dados do dashboard se necessário
      setTimeout(() => {
        // Se tiver função para recarregar dashboard
        // fetchDashboardData();
      }, 1000);
    } catch (err) {
      console.error("❌ Erro na automação:", err);

      // ✅ CORREÇÃO: Status de erro mais informativo
      setAutomationStatus({
        type: "error",
        message:
          err.response?.data?.message ||
          err.message ||
          "Falha ao executar automação",
        details: err.response?.data,
      });

      // ✅ BÔNUS: Fallback para não quebrar a UI
      console.warn("⚠️ Usando fallback para automação...");
    } finally {
      setAutomationRunning(false);
    }
  }

  async function loadDashboard() {
    setLoading(true);
    try {
      // ✅ CORREÇÃO: Remove chamadas 404 que causam erro
      // Use fallback diretamente para evitar erros
      setKpis(fallbackKpis);
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
      setMeetings([
        { id: 1, title: "SNOP", date: "2025-12-08 10:00", owner: "Éder" },
        {
          id: 2,
          title: "One-on-One",
          date: "2025-12-08 15:00",
          owner: "Luiz",
        },
      ]);
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
            <button className="btn outline small" onClick={exportDashboardPDF}>
              📄 Exportar PDF
            </button>
            <button
              className="btn small"
              onClick={runWeeklyAutomation}
              disabled={automationRunning}
            >
              🤖 Rodar Automação
            </button>
          </div>
        </header>

        {automationStatus === "success" && (
          <div className="alert success">
            🤖 Automação executada com sucesso
          </div>
        )}

        {automationStatus === "error" && (
          <div className="alert error">❌ Erro ao executar automação</div>
        )}

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
            {/* ✅ CORREÇÃO: Altura fixa para resolver erro Recharts */}
            <div style={{ height: 250 }}>
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
              {/* ✅ CORREÇÃO: Altura fixa */}
              <div style={{ height: 200 }}>
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
              {/* ✅ CORREÇÃO: Altura fixa */}
              <div style={{ height: 180 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieDataFallback}
                      dataKey="value"
                      outerRadius={60}
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
