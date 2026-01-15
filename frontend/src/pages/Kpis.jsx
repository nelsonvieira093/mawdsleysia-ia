// frontend/src/pages/Kpis.jsx
// VERSÃO FINAL OTIMIZADA - ESTRUTURA REAL + DESIGN MELHORADO

import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { getKpiOverview } from "@/services/kpis";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  Cell
} from "recharts";
import "./Kpis.css";

// =====================================================
// COMPONENTES AUXILIARES
// =====================================================

function MetricCard({ title, value, subtitle, icon = "📊", color = "#007bff" }) {
  return (
    <div className="metric-card" style={{ borderTop: `4px solid ${color}` }}>
      <div className="metric-icon">{icon}</div>
      <div className="metric-content">
        <div className="metric-title">{title}</div>
        <div className="metric-value">{value}</div>
        {subtitle && <div className="metric-subtitle">{subtitle}</div>}
      </div>
    </div>
  );
}

function SummaryCard({ label, value, trend = null }) {
  return (
    <div className="summary-card">
      <span className="summary-label">{label}</span>
      <strong className="summary-value">{value}</strong>
      {trend && <span className={`summary-trend ${trend.type}`}>{trend.value}</span>}
    </div>
  );
}

// =====================================================
// COMPONENTE PRINCIPAL
// =====================================================

export default function Kpis() {
  const [kpisData, setKpisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [usingFallback, setUsingFallback] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // ---------------------------------------------------
  // DADOS DE FALLBACK (ESTRUTURA REAL + COMPATIBILIDADE)
  // ---------------------------------------------------
  const fallbackData = {
    // Estrutura real do backend
    followups: {
      total: 8,
      completed: 3,
      pending: 5,
      overdue: 1,
      completion_rate: 38
    },
    deliverables: {
      total: 12,
      on_time: 9,
      delayed: 3,
      completion_rate: 75,
      quality_score: 88
    },
    meetings: {
      completed: 5,
      scheduled: 3,
      cancelled: 1,
      attendance_rate: 92
    },
    performance: {
      team_velocity: 85,
      customer_satisfaction: 92,
      system_uptime: 99.8,
      response_time_avg: "45ms"
    },
    trends: {
      weekly_growth: "+12%",
      monthly_growth: "+28%",
      quarterly_target: "85%"
    },
    // Compatibilidade com versão antiga
    executive: {
      summary: {
        total_followups: 18,
        overdue_followups: 5,
        meetings_this_week: 7,
      }
    },
    operational: {
      meetings: [
        { user_id: "Ana", total_meetings: 3 },
        { user_id: "Carlos", total_meetings: 5 },
        { user_id: "João", total_meetings: 2 },
      ]
    }
  };

  // Dados para gráficos
  const performanceChartData = [
    { name: "Velocidade", value: 85, color: "#4CAF50" },
    { name: "Qualidade", value: 88, color: "#2196F3" },
    { name: "Satisfação", value: 92, color: "#9C27B0" },
    { name: "Uptime", value: 99.8, color: "#FF9800" }
  ];

  const weeklyMeetingsData = [
    { day: "Seg", meetings: 3, color: "#4CAF50" },
    { day: "Ter", meetings: 5, color: "#2196F3" },
    { day: "Qua", meetings: 4, color: "#9C27B0" },
    { day: "Qui", meetings: 6, color: "#FF9800" },
    { day: "Sex", meetings: 2, color: "#E91E63" }
  ];

  useEffect(() => {
    loadKpis();
  }, []);

  const loadKpis = async () => {
    try {
      setLoading(true);
      const res = await getKpiOverview();
      
      console.log("📊 Dados recebidos do backend:", res);
      
      if (res && res.data) {
        // ✅ COMPATIBILIDADE DUPLA: Suporta ambas estruturas
        if (res.data.data) {
          // Estrutura nova: { success: true, data: {...} }
          setKpisData(res.data.data);
        } else if (res.data.followups || res.data.executive) {
          // Estrutura direta ou antiga
          setKpisData(res.data);
        } else {
          // Tenta usar resposta direta
          setKpisData(res.data);
        }
        setUsingFallback(false);
      } else {
        throw new Error("Resposta inválida da API");
      }
      
    } catch (err) {
      console.warn("⚠️ Usando dados de fallback:", err.message);
      setKpisData(fallbackData);
      setUsingFallback(true);
    } finally {
      setLoading(false);
      setLastUpdate(new Date());
    }
  };

  if (loading) {
    return (
      <div className="kpis-page">
        <Sidebar />
        <main className="kpis-main">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Carregando indicadores estratégicos…</p>
          </div>
        </main>
      </div>
    );
  }

  // ✅ CORREÇÃO: Usa dados reais ou fallback
  const data = kpisData || fallbackData;
  
  // ✅ COMPATIBILIDADE: Extrai dados independente da estrutura
  const followups = data.followups || data.executive?.summary || {};
  const deliverables = data.deliverables || {};
  const meetings = data.meetings || {};
  const performance = data.performance || {};
  const trends = data.trends || {};
  const operationalMeetings = data.operational?.meetings || weeklyMeetingsData.map(m => ({ 
    user_id: m.day, 
    total_meetings: m.meetings 
  }));

  // Converte dados para gráfico de barras
  const chartData = operationalMeetings.map(item => ({
    name: typeof item.user_id === 'number' ? `Usuário ${item.user_id}` : item.user_id,
    meetings: item.total_meetings || 0
  }));

  return (
    <div className="kpis-page">
      <Sidebar />

      <main className="kpis-main">
        {/* HEADER COM CONTROLES */}
        <header className="kpis-header">
          <div className="header-content">
            <h1>
              <span className="header-icon">📊</span>
              KPIs Estratégicos
            </h1>
            <p className="header-subtitle">
              Indicadores em tempo real monitorados pelo Agente MAWDSLEYS
            </p>
          </div>
          
          <div className="header-controls">
            {usingFallback && (
              <div className="fallback-badge">
                <span className="badge-icon">⚠️</span>
                <span className="badge-text">Modo Demonstrativo</span>
              </div>
            )}
            
            <div className="update-info">
              <span className="update-label">Última atualização:</span>
              <span className="update-time">{lastUpdate.toLocaleTimeString()}</span>
            </div>
            
            <button 
              onClick={loadKpis}
              className="refresh-button"
              disabled={loading}
            >
              <span className="button-icon">🔄</span>
              <span className="button-text">Atualizar</span>
            </button>
          </div>
        </header>

        {/* ALERTA DE FALLBACK */}
        {usingFallback && (
          <div className="alert-banner">
            <span className="alert-icon">ℹ️</span>
            <span className="alert-text">
              Dados de demonstração • <a href="#" onClick={(e) => { e.preventDefault(); loadKpis(); }}>Tentar reconectar</a>
            </span>
          </div>
        )}

        {/* SEÇÃO 1: VISÃO GERAL */}
        <section className="overview-section">
          <h2 className="section-title">
            <span className="section-icon">📈</span>
            Visão Geral
          </h2>
          
          <div className="summary-grid">
            <SummaryCard 
              label="Follow-ups Totais" 
              value={followups.total || followups.total_followups || 0}
              trend={{ value: trends.weekly_growth || "+0%", type: "positive" }}
            />
            <SummaryCard 
              label="Entregáveis no Prazo" 
              value={deliverables.on_time || 0}
              trend={{ value: `${deliverables.completion_rate || 0}%`, type: "neutral" }}
            />
            <SummaryCard 
              label="Reuniões Realizadas" 
              value={meetings.completed || 0}
              trend={{ value: `${meetings.attendance_rate || 0}% presença`, type: "positive" }}
            />
            <SummaryCard 
              label="Satisfação do Cliente" 
              value={`${performance.customer_satisfaction || 0}%`}
              trend={{ value: trends.monthly_growth || "+0%", type: "positive" }}
            />
          </div>
        </section>

        {/* SEÇÃO 2: MÉTRICAS DETALHADAS */}
        <section className="metrics-section">
          <h2 className="section-title">
            <span className="section-icon">🎯</span>
            Métricas de Performance
          </h2>
          
          <div className="metrics-grid">
            <MetricCard 
              icon="📋"
              title="Follow-ups"
              value={`${followups.completion_rate || 0}%`}
              subtitle={`${followups.completed || 0} de ${followups.total || 0} concluídos`}
              color="#4CAF50"
            />
            
            <MetricCard 
              icon="📦"
              title="Entregáveis"
              value={`${deliverables.quality_score || 0}%`}
              subtitle={`${deliverables.on_time || 0} no prazo • ${deliverables.delayed || 0} atrasados`}
              color="#2196F3"
            />
            
            <MetricCard 
              icon="⚡"
              title="Velocidade"
              value={`${performance.team_velocity || 0}%`}
              subtitle="Produtividade da equipe"
              color="#9C27B0"
            />
            
            <MetricCard 
              icon="🖥️"
              title="Disponibilidade"
              value={`${performance.system_uptime || 0}%`}
              subtitle="Uptime do sistema"
              color="#FF9800"
            />
          </div>
        </section>

        {/* SEÇÃO 3: GRÁFICOS */}
        <div className="charts-section">
          {/* GRÁFICO 1: REUNIÕES POR USUÁRIO/DIA */}
          <div className="chart-container">
            <div className="chart-header">
              <h3>📅 Reuniões por {chartData[0]?.name?.includes('Usuário') ? 'Usuário' : 'Dia da Semana'}</h3>
              <span className="chart-subtitle">Distribuição semanal</span>
            </div>
            
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="name" 
                    tick={{ fill: '#666' }}
                    axisLine={{ stroke: '#ddd' }}
                  />
                  <YAxis 
                    tick={{ fill: '#666' }}
                    axisLine={{ stroke: '#ddd' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                  <Bar 
                    dataKey="meetings" 
                    name="Reuniões"
                    radius={[4, 4, 0, 0]}
                  >
                    {chartData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={weeklyMeetingsData[index]?.color || '#8884d8'} 
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* GRÁFICO 2: PERFORMANCE */}
          <div className="chart-container">
            <div className="chart-header">
              <h3>📊 Indicadores de Performance</h3>
              <span className="chart-subtitle">Métricas principais</span>
            </div>
            
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={performanceChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="name" 
                    tick={{ fill: '#666' }}
                    axisLine={{ stroke: '#ddd' }}
                  />
                  <YAxis 
                    domain={[0, 100]}
                    tick={{ fill: '#666' }}
                    axisLine={{ stroke: '#ddd' }}
                  />
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'Score']}
                    contentStyle={{ 
                      backgroundColor: 'white',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                  <Bar 
                    dataKey="value" 
                    name="Score"
                    radius={[4, 4, 0, 0]}
                  >
                    {performanceChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* SEÇÃO 4: TENDÊNCIAS E METAS */}
        <section className="trends-section">
          <h2 className="section-title">
            <span className="section-icon">🚀</span>
            Tendências e Metas
          </h2>
          
          <div className="trends-grid">
            <div className="trend-card positive">
              <div className="trend-icon">📈</div>
              <div className="trend-content">
                <div className="trend-title">Crescimento Semanal</div>
                <div className="trend-value">{trends.weekly_growth || "+0%"}</div>
              </div>
            </div>
            
            <div className="trend-card positive">
              <div className="trend-icon">📊</div>
              <div className="trend-content">
                <div className="trend-title">Crescimento Mensal</div>
                <div className="trend-value">{trends.monthly_growth || "+0%"}</div>
              </div>
            </div>
            
            <div className="trend-card target">
              <div className="trend-icon">🎯</div>
              <div className="trend-content">
                <div className="trend-title">Meta Trimestral</div>
                <div className="trend-value">{trends.quarterly_target || "0%"}</div>
                <div className="trend-subtitle">Atingimento</div>
              </div>
            </div>
            
            <div className="trend-card neutral">
              <div className="trend-icon">⏱️</div>
              <div className="trend-content">
                <div className="trend-title">Tempo de Resposta</div>
                <div className="trend-value">{performance.response_time_avg || "0ms"}</div>
                <div className="trend-subtitle">Média do sistema</div>
              </div>
            </div>
          </div>
        </section>

        {/* FOOTER INFORMATIVO */}
        <footer className="kpis-footer">
          <div className="footer-content">
            <div className="footer-text">
              <strong>Sistema MAWDSLEYS</strong> • Indicadores atualizados automaticamente
            </div>
            <div className="footer-actions">
              <button 
                onClick={loadKpis}
                className="footer-button"
                disabled={loading}
              >
                {loading ? 'Atualizando...' : '🔄 Atualizar Agora'}
              </button>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}