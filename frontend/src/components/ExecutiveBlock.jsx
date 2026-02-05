// frontend/src/components/ExecutiveBlock.jsx - VERSÃO FINAL CORRIGIDA COM MELHORIAS
import React, { useState, useEffect } from "react";
import "./ExecutiveBlock.css";

export default function ExecutiveBlock({ data }) {
  const [showDebug, setShowDebug] = useState(false);
  const [processedData, setProcessedData] = useState(null);

  useEffect(() => {
    // 🔥 CORREÇÃO: Processa os dados quando chegam
    if (!data) {
      console.log("❌ ExecutiveBlock: Nenhum data fornecido");
      setProcessedData(null);
      return;
    }

    console.log("🔍 ExecutiveBlock recebeu dados:", {
      type: typeof data,
      keys: Object.keys(data || {}),
      hasSummary: !!data.summary,
      hasContent: !!data.content,
    });

    // Se data for string (erro no processamento)
    if (typeof data === "string") {
      console.log("⚠️ ExecutiveBlock: data é string, criando estrutura básica");
      setProcessedData({
        hashtags: ["Sistema"],
        summary: data.length > 200 ? data.substring(0, 200) + "..." : data,
        structured_summary: "",
        followups: [],
        rituals: [],
        directors: [],
        actions: [],
        register_location: "DailyLog",
        raw_text: "",
      });
      return;
    }

    // 🔥 CORREÇÃO: Limpa raw_text se for JSON
    const cleanData = { ...data };

    if (cleanData.raw_text && typeof cleanData.raw_text === "string") {
      // Se raw_text for JSON, limpa
      if (
        cleanData.raw_text.trim().startsWith("{") ||
        cleanData.raw_text.trim().startsWith("[")
      ) {
        try {
          JSON.parse(cleanData.raw_text);
          // Se for JSON válido, substitui por texto limpo
          cleanData.raw_text = "Dados processados automaticamente";
        } catch (e) {
          // Não é JSON válido, mantém como está
          console.log("Raw text não é JSON válido, mantendo");
        }
      }
    }

    // 🔥 CORREÇÃO: Garante estrutura mínima
    const finalData = {
      // Informações básicas
      hashtags: Array.isArray(cleanData.hashtags)
        ? cleanData.hashtags
        : cleanData.tags
          ? cleanData.tags
          : ["Executivo"],
      summary:
        cleanData.summary ||
        cleanData.structured_summary ||
        cleanData.content ||
        "Análise executiva processada",
      structured_summary:
        cleanData.structured_summary || cleanData.summary || "",

      // Arrays garantidos
      followups: Array.isArray(cleanData.followups) ? cleanData.followups : [],
      tasks: Array.isArray(cleanData.tasks) ? cleanData.tasks : [],
      subtasks: Array.isArray(cleanData.subtasks) ? cleanData.subtasks : [],
      rituals: Array.isArray(cleanData.rituals)
        ? cleanData.rituals
        : cleanData.ritual
          ? Array.isArray(cleanData.ritual)
            ? cleanData.ritual
            : [cleanData.ritual]
          : [],
      directors: Array.isArray(cleanData.directors)
        ? cleanData.directors
        : cleanData.departments || [],
      actions: Array.isArray(cleanData.actions)
        ? cleanData.actions
        : cleanData.actions_required || cleanData.tasks || [],

      // Campos obrigatórios com fallback
      register_location:
        cleanData.register_location ||
        cleanData.where_to_register ||
        "DailyLog",
      raw_text: cleanData.raw_text || "",

      // Campos opcionais com fallback seguro
      timestamp: cleanData.timestamp,
      created_at: cleanData.created_at,
      time_estimate: cleanData.time_estimate,
      deadline: cleanData.deadline,
      priority: cleanData.priority,
      urgency: cleanData.urgency,
      impact: cleanData.impact,
      complexity: cleanData.complexity,
      budget_impact: cleanData.budget_impact,
      revenue_impact: cleanData.revenue_impact,
      cost_estimate: cleanData.cost_estimate,
      roi_estimate: cleanData.roi_estimate,
      resources_needed: Array.isArray(cleanData.resources_needed)
        ? cleanData.resources_needed
        : [],
      team_members: Array.isArray(cleanData.team_members)
        ? cleanData.team_members
        : [],
      departments: Array.isArray(cleanData.departments)
        ? cleanData.departments
        : [],
      metrics: Array.isArray(cleanData.metrics) ? cleanData.metrics : [],
      kpis: Array.isArray(cleanData.kpis) ? cleanData.kpis : [],
      success_criteria: Array.isArray(cleanData.success_criteria)
        ? cleanData.success_criteria
        : [],
      risks: Array.isArray(cleanData.risks) ? cleanData.risks : [],
      dependencies: Array.isArray(cleanData.dependencies)
        ? cleanData.dependencies
        : [],
      blockers: Array.isArray(cleanData.blockers) ? cleanData.blockers : [],
      decisions: Array.isArray(cleanData.decisions) ? cleanData.decisions : [],
      recommendations: Array.isArray(cleanData.recommendations)
        ? cleanData.recommendations
        : [],
      alternatives: Array.isArray(cleanData.alternatives)
        ? cleanData.alternatives
        : [],
      related_documents: Array.isArray(cleanData.related_documents)
        ? cleanData.related_documents
        : [],
      references: Array.isArray(cleanData.references)
        ? cleanData.references
        : [],
      categories: Array.isArray(cleanData.categories)
        ? cleanData.categories
        : [],
      projects: Array.isArray(cleanData.projects) ? cleanData.projects : [],
      initiatives: Array.isArray(cleanData.initiatives)
        ? cleanData.initiatives
        : [],
      sentiment: cleanData.sentiment,
      confidence_score: cleanData.confidence_score,
      ai_insights: Array.isArray(cleanData.ai_insights)
        ? cleanData.ai_insights
        : [],
    };

    console.log("✅ ExecutiveBlock dados processados:", {
      hashtags: finalData.hashtags.length,
      summaryLength: finalData.summary?.length,
      followups: finalData.followups.length,
      actions: finalData.actions.length,
      rituals: finalData.rituals.length,
      priority: finalData.priority,
      deadline: finalData.deadline,
    });

    setProcessedData(finalData);
  }, [data]);

  if (!processedData) {
    return (
      <div
        className="executive-block error"
        style={{
          padding: "20px",
          textAlign: "center",
          color: "#f87171",
          background: "rgba(239, 68, 68, 0.1)",
          borderRadius: "8px",
          border: "1px solid rgba(239, 68, 68, 0.3)",
        }}
      >
        <div style={{ fontSize: "24px", marginBottom: "10px" }}>⏳</div>
        <div>Processando dados executivos...</div>
      </div>
    );
  }

  // Processa dados para renderização
  const {
    // Informações básicas
    hashtags = [],
    summary,
    structured_summary,
    raw_text,

    // Timeline e datas
    timestamp,
    created_at,
    time_estimate,
    deadline,

    // Prioridades
    priority,
    urgency,
    impact,
    complexity,

    // Dados financeiros
    budget_impact,
    revenue_impact,
    cost_estimate,
    roi_estimate,

    // Recursos
    resources_needed = [],
    team_members = [],
    departments = [],

    // Follow-ups e tarefas
    followups = [],
    tasks = [],
    subtasks = [],

    // Métricas e KPIs
    metrics = [],
    kpis = [],
    success_criteria = [],

    // Riscos
    risks = [],
    dependencies = [],
    blockers = [],

    // Decisões
    decisions = [],
    recommendations = [],
    alternatives = [],

    // Documentação
    related_documents = [],
    references = [],

    // Categorização
    categories = [],
    projects = [],
    initiatives = [],

    // Campos do seu sistema atual
    rituals = [],
    directors = [],
    actions = [],
    register_location,

    // Campos adicionais
    sentiment,
    confidence_score,
    ai_insights = [],
  } = processedData;

  // 🔥 MELHORIA: Síntese otimizada com truncamento inteligente
  const finalSummary =
    (summary || structured_summary || "Análise executiva gerada")
      .substring(0, 200)
      .trim() +
    ((summary || structured_summary || "").length > 200 ? "..." : "");

  const finalRituals = Array.isArray(rituals) && rituals.length ? rituals : [];
  const allCategories = [...hashtags, ...categories].filter(Boolean);
  const allTeamMembers = [...team_members, ...directors].filter(Boolean);
  const allActions = [...actions, ...tasks].filter(Boolean);
  const allFollowups = [...followups, ...subtasks].filter(Boolean);

  // 🔥 MELHORIA: Formatação de data para deadline
  const formatDeadline = (dateStr) => {
    if (!dateStr) return "";

    try {
      // Tenta parsear datas em diferentes formatos
      if (typeof dateStr === "string") {
        // Para datas como "segunda-feira", "amanhã"
        if (dateStr.toLowerCase().includes("amanhã")) {
          const tomorrow = new Date();
          tomorrow.setDate(tomorrow.getDate() + 1);
          return tomorrow.toLocaleDateString("pt-BR");
        }

        // Para dias da semana
        const weekdays = {
          segunda: 1,
          terça: 2,
          quarta: 3,
          quinta: 4,
          sexta: 5,
          sábado: 6,
          domingo: 0,
        };

        for (const [weekday, dayOffset] of Object.entries(weekdays)) {
          if (dateStr.toLowerCase().includes(weekday)) {
            const today = new Date();
            const targetDay = new Date(today);
            const daysUntilTarget = (dayOffset - today.getDay() + 7) % 7;
            targetDay.setDate(today.getDate() + daysUntilTarget);
            return targetDay.toLocaleDateString("pt-BR");
          }
        }

        // Para datas no formato DD/MM ou DD/MM/YYYY
        if (dateStr.match(/\d{1,2}\/\d{1,2}(\/\d{4})?/)) {
          const parts = dateStr.split("/");
          if (parts.length === 2) {
            // DD/MM - assume ano atual
            const year = new Date().getFullYear();
            const date = new Date(year, parts[1] - 1, parts[0]);
            return date.toLocaleDateString("pt-BR");
          } else if (parts.length === 3) {
            // DD/MM/YYYY
            const date = new Date(parts[2], parts[1] - 1, parts[0]);
            return date.toLocaleDateString("pt-BR");
          }
        }
      }

      // Fallback: tenta criar Date normalmente
      return new Date(dateStr).toLocaleDateString("pt-BR");
    } catch (e) {
      console.log("⚠️ Erro ao formatar deadline:", dateStr, e);
      return dateStr; // Retorna string original se não conseguir formatar
    }
  };

  // 🔥 MELHORIA: Calcula tempo restante se houver deadline
  const calculateTimeRemaining = (deadlineStr) => {
    if (!deadlineStr) return null;

    try {
      let deadlineDate;

      if (typeof deadlineStr === "string") {
        // Tenta parsear a data formatada
        const formatted = formatDeadline(deadlineStr);
        deadlineDate = new Date(formatted);
      } else {
        deadlineDate = new Date(deadlineStr);
      }

      if (isNaN(deadlineDate.getTime())) return null;

      const today = new Date();
      today.setHours(0, 0, 0, 0);
      deadlineDate.setHours(0, 0, 0, 0);

      const diffTime = deadlineDate - today;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      if (diffDays === 0) return "hoje";
      if (diffDays === 1) return "amanhã";
      if (diffDays === -1) return "ontem";
      if (diffDays < 0) return `há ${Math.abs(diffDays)} dias`;
      return `em ${diffDays} dias`;
    } catch (e) {
      return null;
    }
  };

  const timeRemaining = calculateTimeRemaining(deadline);

  return (
    <div className="executive-block">
      {/* 🔥 BOTÃO DE DEBUG - SÓ VISÍVEL EM DESENVOLVIMENTO */}
      {process.env.NODE_ENV === "development" && (
        <div
          style={{
            position: "absolute",
            top: "10px",
            right: "10px",
            zIndex: 10,
          }}
        >
          <button
            onClick={() => setShowDebug(!showDebug)}
            style={{
              background: showDebug
                ? "rgba(59, 130, 246, 0.2)"
                : "rgba(59, 130, 246, 0.1)",
              border: "1px solid rgba(59, 130, 246, 0.3)",
              color: "#60a5fa",
              borderRadius: "6px",
              padding: "4px 12px",
              fontSize: "11px",
              cursor: "pointer",
              fontWeight: "600",
              display: "flex",
              alignItems: "center",
              gap: "5px",
              transition: "all 0.2s",
            }}
          >
            {showDebug ? "🔒 Ocultar Debug" : "🔓 Mostrar Debug"}
          </button>
        </div>
      )}

      {/* CABEÇALHO COMPLETO */}
      <div className="executive-header">
        <div className="header-main">
          <h3>📊 Análise Executiva Completa</h3>
          <div className="header-meta">
            {timestamp && (
              <span className="meta-item">
                📅 {new Date(timestamp).toLocaleDateString("pt-BR")}
              </span>
            )}
            {priority && (
              <span
                className={`priority-badge priority-${priority.toLowerCase()}`}
              >
                {priority}
              </span>
            )}
            {confidence_score && (
              <span className="confidence-score">
                🎯 {Math.min(Math.max(confidence_score, 0), 100)}% de confiança
              </span>
            )}
          </div>
        </div>

        {/* HASHTAGS E CATEGORIAS */}
        <div className="executive-tags">
          {allCategories.length > 0 ? (
            allCategories.map((tag, index) => (
              <span key={index} className="exec-tag">
                #{tag}
              </span>
            ))
          ) : (
            <span className="exec-tag muted">#Executivo</span>
          )}
        </div>
      </div>

      {/* GRID PRINCIPAL DE INFORMAÇÕES */}
      <div className="executive-grid">
        {/* COLUNA 1: VISÃO GERAL */}
        <div className="grid-column">
          <div className="info-card">
            <h4>🎯 Visão Geral</h4>
            <div className="card-content">
              <div className="summary-box">
                <h5>Síntese Executiva</h5>
                <p>{finalSummary}</p>
              </div>

              {/* PRIORIZAÇÃO */}
              {(priority || urgency || impact || complexity) && (
                <div className="priority-section">
                  <h5>Priorização</h5>
                  <div className="priority-grid">
                    {priority && (
                      <div className="priority-item">
                        <span className="label">Prioridade:</span>
                        <span
                          className={`value priority-${priority.toLowerCase()}`}
                        >
                          {priority}
                        </span>
                      </div>
                    )}
                    {urgency && (
                      <div className="priority-item">
                        <span className="label">Urgência:</span>
                        <span className="value">{urgency}/10</span>
                      </div>
                    )}
                    {impact && (
                      <div className="priority-item">
                        <span className="label">Impacto:</span>
                        <span className="value">{impact}/10</span>
                      </div>
                    )}
                    {complexity && (
                      <div className="priority-item">
                        <span className="label">Complexidade:</span>
                        <span className="value">{complexity}/10</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* TIMELINE */}
          {(deadline || time_estimate || created_at) && (
            <div className="info-card">
              <h4>⏰ Timeline</h4>
              <div className="card-content">
                {deadline && (
                  <div className="timeline-item">
                    <span className="label">Prazo Final:</span>
                    <span className="value deadline">
                      {formatDeadline(deadline)}
                      {timeRemaining && (
                        <span
                          style={{
                            marginLeft: "8px",
                            fontSize: "11px",
                            background:
                              timeRemaining.includes("hoje") ||
                              timeRemaining.includes("amanhã")
                                ? "rgba(239, 68, 68, 0.2)"
                                : "rgba(34, 197, 94, 0.2)",
                            color:
                              timeRemaining.includes("hoje") ||
                              timeRemaining.includes("amanhã")
                                ? "#f87171"
                                : "#22c55e",
                            padding: "2px 6px",
                            borderRadius: "4px",
                            fontWeight: "600",
                          }}
                        >
                          ({timeRemaining})
                        </span>
                      )}
                    </span>
                  </div>
                )}
                {time_estimate && (
                  <div className="timeline-item">
                    <span className="label">Estimativa:</span>
                    <span className="value">{time_estimate}</span>
                  </div>
                )}
                {created_at && (
                  <div className="timeline-item">
                    <span className="label">Criado em:</span>
                    <span className="value">
                      {new Date(created_at).toLocaleDateString("pt-BR")}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* COLUNA 2: RECURSOS E EQUIPE */}
        <div className="grid-column">
          {/* RECURSOS NECESSÁRIOS */}
          {(resources_needed.length > 0 ||
            allTeamMembers.length > 0 ||
            departments.length > 0) && (
            <div className="info-card">
              <h4>👥 Recursos & Equipe</h4>
              <div className="card-content">
                {allTeamMembers.length > 0 && (
                  <div className="team-section">
                    <h5>Equipe Envolvida</h5>
                    <div className="team-list">
                      {allTeamMembers.map((member, index) => (
                        <span key={index} className="team-member">
                          👤 {member}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {resources_needed.length > 0 && (
                  <div className="resources-section">
                    <h5>Recursos Necessários</h5>
                    <ul className="resources-list">
                      {resources_needed.map((resource, index) => (
                        <li key={index}>{resource}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {departments.length > 0 && (
                  <div className="departments-section">
                    <h5>Departamentos</h5>
                    <div className="departments-list">
                      {departments.map((dept, index) => (
                        <span key={index} className="department-tag">
                          🏢 {dept}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* RITOS E PROCESSOS */}
          {finalRituals.length > 0 && (
            <div className="info-card">
              <h4>🔄 Ritos Relacionados</h4>
              <div className="card-content">
                <div className="rituals-list">
                  {finalRituals.map((ritual, index) => (
                    <div key={index} className="ritual-item">
                      🔄 {ritual}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* COLUNA 3: AÇÕES E FOLLOW-UPS */}
        <div className="grid-column">
          {/* AÇÕES E TAREFAS */}
          {allActions.length > 0 && (
            <div className="info-card">
              <h4>✅ Ações & Tarefas</h4>
              <div className="card-content">
                <ul className="actions-list">
                  {allActions.slice(0, 8).map((action, index) => {
                    // 🔥 MELHORIA: Marca ações urgentes
                    const isUrgent =
                      action.toLowerCase().includes("urgente") ||
                      action.toLowerCase().includes("hoje") ||
                      action.toLowerCase().includes("asap");

                    return (
                      <li key={index} className="action-item">
                        <span className="action-checkbox">
                          {isUrgent ? "🚨" : "☐"}
                        </span>
                        <span
                          className="action-text"
                          style={{
                            color: isUrgent ? "#f87171" : "inherit",
                            fontWeight: isUrgent ? "600" : "inherit",
                          }}
                        >
                          {action}
                        </span>
                      </li>
                    );
                  })}
                </ul>
                {allActions.length > 8 && (
                  <div className="more-items">
                    + {allActions.length - 8} mais ações...
                  </div>
                )}
              </div>
            </div>
          )}

          {/* FOLLOW-UPS */}
          {allFollowups.length > 0 && (
            <div className="info-card">
              <h4>📋 Follow-ups Identificados</h4>
              <div className="card-content">
                <ul className="followups-list">
                  {allFollowups.slice(0, 6).map((followup, index) => {
                    // 🔥 MELHORIA: Destaque para follow-ups prioritários
                    const isHighPriority =
                      followup.toLowerCase().includes("importante") ||
                      followup.toLowerCase().includes("priorit");

                    return (
                      <li key={index} className="followup-item">
                        <span className="followup-icon">
                          {isHighPriority ? "🚨" : "📌"}
                        </span>
                        <span
                          className="followup-text"
                          style={{
                            color: isHighPriority ? "#fbbf24" : "inherit",
                          }}
                        >
                          {followup}
                        </span>
                      </li>
                    );
                  })}
                </ul>
                {allFollowups.length > 6 && (
                  <div className="more-items">
                    + {allFollowups.length - 6} mais follow-ups...
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* COLUNA 4: IMPACTO E MÉTRICAS */}
        <div className="grid-column">
          {/* IMPACTO FINANCEIRO */}
          {(budget_impact ||
            revenue_impact ||
            cost_estimate ||
            roi_estimate) && (
            <div className="info-card">
              <h4>💰 Impacto Financeiro</h4>
              <div className="card-content">
                <div className="financial-grid">
                  {budget_impact && (
                    <div className="financial-item">
                      <span className="label">Impacto Orçamentário:</span>
                      <span
                        className={`value ${typeof budget_impact === "string" && budget_impact.includes("-") ? "negative" : "positive"}`}
                      >
                        {budget_impact}
                      </span>
                    </div>
                  )}
                  {revenue_impact && (
                    <div className="financial-item">
                      <span className="label">Impacto em Receita:</span>
                      <span
                        className={`value ${typeof revenue_impact === "string" && revenue_impact.includes("-") ? "negative" : "positive"}`}
                      >
                        {revenue_impact}
                      </span>
                    </div>
                  )}
                  {cost_estimate && (
                    <div className="financial-item">
                      <span className="label">Custo Estimado:</span>
                      <span className="value">{cost_estimate}</span>
                    </div>
                  )}
                  {roi_estimate && (
                    <div className="financial-item">
                      <span className="label">ROI Estimado:</span>
                      <span className="value positive">{roi_estimate}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* MÉTRICAS E KPIs */}
          {(metrics.length > 0 || kpis.length > 0) && (
            <div className="info-card">
              <h4>📈 Métricas & KPIs</h4>
              <div className="card-content">
                <div className="metrics-grid">
                  {metrics.slice(0, 4).map((metric, index) => (
                    <div key={index} className="metric-item">
                      <span className="metric-name">
                        {typeof metric === "object" ? metric.name : metric}
                      </span>
                      <span className="metric-value">
                        {typeof metric === "object" ? metric.value : "—"}
                      </span>
                    </div>
                  ))}
                  {kpis.slice(0, 4).map((kpi, index) => (
                    <div key={index} className="kpi-item">
                      <span className="kpi-name">
                        🎯 {typeof kpi === "object" ? kpi.name : kpi}
                      </span>
                      <span className="kpi-value">
                        {typeof kpi === "object" ? kpi.value : "—"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ONDE REGISTRAR */}
          {register_location && (
            <div className="info-card">
              <h4>📝 Registro</h4>
              <div className="card-content">
                <div className="registration-info">
                  <span className="label">Local de Registro:</span>
                  <span className="value highlight">{register_location}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* SEÇÕES ADICIONAIS (se houver dados) */}
      <div className="additional-sections">
        {/* RISCOS */}
        {risks.length > 0 && (
          <div className="section-card danger">
            <h4>⚠️ Riscos Identificados</h4>
            <ul className="risks-list">
              {risks.map((risk, index) => (
                <li key={index} className="risk-item">
                  <span className="risk-icon">⚠️</span>
                  <span className="risk-text">{risk}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* DECISÕES */}
        {decisions.length > 0 && (
          <div className="section-card success">
            <h4>🤔 Decisões Tomadas</h4>
            <ul className="decisions-list">
              {decisions.map((decision, index) => (
                <li key={index} className="decision-item">
                  <span className="decision-icon">✓</span>
                  <span className="decision-text">{decision}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* INSIGHTS DA IA */}
        {ai_insights.length > 0 && (
          <div className="section-card info">
            <h4>🧠 Insights da IA</h4>
            <ul className="insights-list">
              {ai_insights.map((insight, index) => (
                <li key={index} className="insight-item">
                  <span className="insight-icon">💡</span>
                  <span className="insight-text">{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 🔥 SEÇÃO DE DEBUG - APENAS QUANDO ATIVADA EM DESENVOLVIMENTO */}
      {process.env.NODE_ENV === "development" && showDebug && (
        <div
          className="section-card debug"
          style={{
            marginTop: "20px",
            background: "rgba(17, 24, 39, 0.9)",
            border: "1px solid rgba(55, 65, 81, 0.5)",
            borderRadius: "8px",
            overflow: "hidden",
          }}
        >
          <div
            className="debug-header"
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "12px 16px",
              background: "rgba(31, 41, 55, 0.8)",
              borderBottom: "1px solid rgba(55, 65, 81, 0.5)",
            }}
          >
            <h4 style={{ margin: 0, fontSize: "14px", color: "#9ca3af" }}>
              🔧 Dados Técnicos (Debug)
            </h4>
            <button
              onClick={() => setShowDebug(false)}
              style={{
                background: "transparent",
                border: "none",
                color: "#9ca3af",
                cursor: "pointer",
                fontSize: "12px",
                padding: "4px 8px",
                borderRadius: "4px",
                display: "flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              <span style={{ fontSize: "16px" }}>✕</span> Fechar
            </button>
          </div>
          <div className="raw-data" style={{ padding: "16px" }}>
            <pre
              style={{
                fontSize: "11px",
                maxHeight: "300px",
                overflow: "auto",
                padding: "12px",
                background: "#111827",
                borderRadius: "6px",
                border: "1px solid #374151",
                color: "#d1d5db",
                lineHeight: "1.4",
                margin: 0,
              }}
            >
              {JSON.stringify(
                {
                  // Dados processados
                  processed: {
                    summaryLength: summary?.length,
                    hashtagsCount: hashtags?.length,
                    actionsCount: actions?.length,
                    followupsCount: followups?.length,
                    directorsCount: directors?.length,
                    ritualsCount: rituals?.length,
                    deadline: deadline,
                    priority: priority,
                  },
                  // Informações do processamento
                  processing: {
                    receivedDataType: typeof data,
                    processedDataType: typeof processedData,
                    timestamp: new Date().toISOString(),
                  },
                  // Campos principais
                  fields: {
                    summary:
                      summary?.substring(0, 100) +
                      (summary?.length > 100 ? "..." : ""),
                    register_location,
                    hashtags,
                    formattedDeadline: formatDeadline(deadline),
                    timeRemaining: timeRemaining,
                  },
                },
                null,
                2,
              )}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
