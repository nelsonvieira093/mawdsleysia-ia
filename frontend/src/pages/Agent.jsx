import React, { useState, useEffect, useRef } from "react";
import Sidebar from "../components/Sidebar";
import "./Agent.css";

export default function Agent() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [documents, setDocuments] = useState([]);
  const [analysisResult, setAnalysisResult] = useState("");
  const [query, setQuery] = useState("");
  const [chatMessages, setChatMessages] = useState([
    { id: 1, sender: "agent", text: "Olá! Sou o Agente MAWDSLEYS. Como posso ajudar você hoje?" },
  ]);
  const [loading, setLoading] = useState(false);
  const [followUps, setFollowUps] = useState([]);
  const [weeklyAgenda, setWeeklyAgenda] = useState([]);
  const [uploadedFile, setUploadedFile] = useState(null);
  const chatContainerRef = useRef(null);
  const fileInputRef = useRef(null);

  // Dados iniciais
  useEffect(() => {
    // Documentos de exemplo
    const initialDocs = [
      { id: 1, name: "Relatório Financeiro Q3 2025", type: "pdf", size: "2.4 MB", date: "2025-11-15", category: "Financeiro" },
      { id: 2, name: "Contrato Fornecedor XYZ", type: "docx", size: "1.8 MB", date: "2025-11-18", category: "Jurídico" },
      { id: 3, name: "Planejamento Estratégico 2026", type: "pptx", size: "5.2 MB", date: "2025-11-20", category: "Estratégico" },
      { id: 4, name: "Análise de Mercado", type: "xlsx", size: "3.1 MB", date: "2025-11-22", category: "Marketing" },
      { id: 5, name: "Relatório de Infraestrutura", type: "pdf", size: "4.5 MB", date: "2025-11-25", category: "TI" },
    ];
    
    // Follow-ups gerados automaticamente
    const initialFollowUps = [
      { id: 1, title: "Revisar orçamento 2026", priority: "alta", dueDate: "2025-12-10", responsible: "Financeiro", status: "pendente" },
      { id: 2, title: "Renovar certificados SSL", priority: "média", dueDate: "2025-12-05", responsible: "TI", status: "pendente" },
      { id: 3, title: "Atualizar política de privacidade", priority: "alta", dueDate: "2025-12-15", responsible: "Jurídico", status: "em_andamento" },
    ];
    
    // Pauta semanal
    const initialAgenda = [
      { id: 1, day: "Segunda", time: "09:00", title: "Reunião de alinhamento", participants: 5, priority: "média" },
      { id: 2, day: "Terça", time: "14:00", title: "Apresentação de resultados", participants: 8, priority: "alta" },
      { id: 3, day: "Quarta", time: "10:30", title: "Planejamento trimestral", participants: 6, priority: "alta" },
      { id: 4, day: "Quinta", time: "16:00", title: "Treinamento da equipe", participants: 12, priority: "média" },
      { id: 5, day: "Sexta", time: "11:00", title: "Revisão de processos", participants: 4, priority: "baixa" },
    ];

    setDocuments(initialDocs);
    setFollowUps(initialFollowUps);
    setWeeklyAgenda(initialAgenda);
  }, []);

  // Scroll automático no chat
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages]);

  // Função para analisar documentos
  const analyzeDocument = (document) => {
    setLoading(true);
    
    // Simulação de análise de IA
    setTimeout(() => {
      const insights = [
        "📊 **Principais insights detectados:**",
        "• O documento apresenta crescimento de 15% nas receitas do trimestre",
        "• Há uma oportunidade de redução de custos em 8% no próximo semestre",
        "• Foram identificados 3 riscos potenciais que requerem atenção",
        "• Recomenda-se revisão da cláusula 4.2 do contrato",
        "• Timeline do projeto pode ser otimizado em 2 semanas"
      ].join('\n');
      
      setAnalysisResult(insights);
      setActiveTab("analysis");
      
      // Adiciona follow-up automaticamente baseado na análise
      const newFollowUp = {
        id: Date.now(),
        title: `Revisar insights de "${document.name}"`,
        priority: "média",
        dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        responsible: "Gestor",
        status: "pendente"
      };
      
      setFollowUps(prev => [...prev, newFollowUp]);
      
      // Adiciona ao chat
      setChatMessages(prev => [
        ...prev,
        { 
          id: Date.now(), 
          sender: "agent", 
          text: `Analisei o documento "${document.name}" e extraí insights importantes. Também criei um follow-up para revisão.`
        }
      ]);
      
      setLoading(false);
    }, 1500);
  };

  // Função para processar consultas estratégicas
  const handleStrategicQuery = () => {
    if (!query.trim()) return;
    
    setLoading(true);
    
    // Adiciona mensagem do usuário
    const userMessage = { id: Date.now(), sender: "user", text: query };
    setChatMessages(prev => [...prev, userMessage]);
    
    // Simulação de processamento de IA
    setTimeout(() => {
      const responses = {
        "quais são os riscos": "Identifiquei 5 riscos principais: 1) Dependência de fornecedor único 2) Conformidade regulatória 3) Flutuação cambial 4) Retenção de talentos 5) Cibersegurança. Recomendo ação imediata nos itens 2 e 5.",
        "crescimento do mercado": "O mercado apresenta crescimento de 12% ao ano. Nossa participação atual é de 8%, com potencial para 15% em 18 meses. Recomendo expansão nas regiões Sudeste e Sul.",
        "otimização de processos": "Analisei nossos processos principais. Identifiquei oportunidades de automação que podem reduzir custos em 25% e aumentar eficiência em 40%. Vou elaborar um plano detalhado.",
        "análise de concorrência": "Nossos principais concorrentes aumentaram investimento em inovação em 30%. Sugiro: 1) Aumentar R&D em 15% 2) Parcerias estratégicas 3) Diferenciação por serviço premium.",
        "tendências do setor": "Tendências atuais: 1) IA generativa 2) Sustentabilidade ESG 3) Trabalho remoto híbrido 4) Hiperautomação 5) Experiência do cliente omnichannel."
      };
      
      const lowerQuery = query.toLowerCase();
      let response = "Entendi sua consulta. Com base na análise dos dados internos e tendências de mercado, recomendo:\n\n";
      
      if (lowerQuery.includes("risco")) {
        response = responses["quais são os riscos"];
      } else if (lowerQuery.includes("crescimento") || lowerQuery.includes("mercado")) {
        response = responses["crescimento do mercado"];
      } else if (lowerQuery.includes("processo") || lowerQuery.includes("otimiz")) {
        response = responses["otimização de processos"];
      } else if (lowerQuery.includes("concorrência") || lowerQuery.includes("concorrente")) {
        response = responses["análise de concorrência"];
      } else if (lowerQuery.includes("tendência") || lowerQuery.includes("setor")) {
        response = responses["tendências do setor"];
      } else {
        response = `Analisei sua consulta sobre "${query}". Baseado em dados internos e benchmarks do setor, minha recomendação é focar em:\n1. Coleta de dados mais granular\n2. Automação de processos repetitivos\n3. Análise preditiva para tomada de decisão\n4. Integração entre departamentos`;
      }
      
      const agentMessage = { id: Date.now() + 1, sender: "agent", text: response };
      setChatMessages(prev => [...prev, agentMessage]);
      setQuery("");
      setLoading(false);
    }, 2000);
  };

  // Função para gerar pauta semanal automática
  const generateWeeklyAgenda = () => {
    setLoading(true);
    
    setTimeout(() => {
      const newAgenda = [
        { id: 1, day: "Segunda", time: "09:00", title: "Reunião de alinhamento semanal", participants: 6, priority: "média" },
        { id: 2, day: "Segunda", time: "14:30", title: "Análise de métricas do último mês", participants: 4, priority: "alta" },
        { id: 3, day: "Terça", time: "10:00", title: "Apresentação para novo cliente", participants: 8, priority: "alta" },
        { id: 4, day: "Quarta", time: "11:00", title: "Workshop de inovação", participants: 12, priority: "média" },
        { id: 5, day: "Quarta", time: "15:00", title: "Revisão de contratos", participants: 3, priority: "baixa" },
        { id: 6, day: "Quinta", time: "09:30", title: "Treinamento de novas ferramentas", participants: 10, priority: "média" },
        { id: 7, day: "Sexta", time: "16:00", title: "Retrospectiva da semana", participants: 7, priority: "média" },
      ];
      
      setWeeklyAgenda(newAgenda);
      
      // Adiciona ao chat
      setChatMessages(prev => [
        ...prev,
        { 
          id: Date.now(), 
          sender: "agent", 
          text: "Gerada nova pauta semanal otimizada! Inclui reuniões estratégicas, análises de desempenho e sessões de inovação."
        }
      ]);
      
      setLoading(false);
    }, 1800);
  };

  // Função para gerar follow-ups automáticos
  const generateAutoFollowUps = () => {
    setLoading(true);
    
    setTimeout(() => {
      const newFollowUps = [
        { id: Date.now(), title: "Revisar KPIs do trimestre", priority: "alta", dueDate: "2025-12-08", responsible: "Gestor", status: "pendente" },
        { id: Date.now() + 1, title: "Atualizar documentação de segurança", priority: "alta", dueDate: "2025-12-12", responsible: "TI", status: "pendente" },
        { id: Date.now() + 2, title: "Preparar apresentação para board", priority: "média", dueDate: "2025-12-15", responsible: "Comunicação", status: "pendente" },
        { id: Date.now() + 3, title: "Renovar licenças de software", priority: "média", dueDate: "2025-12-20", responsible: "Financeiro", status: "pendente" },
      ];
      
      setFollowUps(prev => [...prev, ...newFollowUps]);
      
      // Adiciona ao chat
      setChatMessages(prev => [
        ...prev,
        { 
          id: Date.now() + 4, 
          sender: "agent", 
          text: "Gerados 4 novos follow-ups baseados em análises recentes e prazos críticos detectados."
        }
      ]);
      
      setLoading(false);
    }, 1500);
  };

  // Função para upload de arquivo
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile(file);
      
      // Simular análise após upload
      setTimeout(() => {
        analyzeDocument({
          id: Date.now(),
          name: file.name,
          type: file.type.split('/')[1],
          size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
          date: new Date().toISOString().split('T')[0],
          category: "Upload"
        });
      }, 1000);
    }
  };

  // Função para enviar mensagem no chat
  const sendMessage = (text) => {
    if (!text.trim()) return;
    
    const userMessage = { id: Date.now(), sender: "user", text };
    setChatMessages(prev => [...prev, userMessage]);
    
    // Resposta automática do agente
    setTimeout(() => {
      const responses = [
        "Entendi. Vou analisar essa informação e trazer insights relevantes.",
        "Baseado nos dados que tenho, posso sugerir algumas ações estratégicas.",
        "Isso é interessante. Deixe-me cruzar com outras informações internas.",
        "Perfeito. Estou processando essa solicitação e já identificando oportunidades.",
        "Obrigado pela informação. Estou gerando recomendações personalizadas."
      ];
      
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      const agentMessage = { id: Date.now() + 1, sender: "agent", text: randomResponse };
      setChatMessages(prev => [...prev, agentMessage]);
    }, 1000);
  };

  // Funções rápidas do chat
  const quickActions = [
    { label: "Analisar riscos", query: "Quais são os principais riscos que devemos considerar?" },
    { label: "Crescimento", query: "Como podemos acelerar nosso crescimento no mercado?" },
    { label: "Otimizar processos", query: "Quais processos podemos otimizar para reduzir custos?" },
    { label: "Tendências", query: "Quais as tendências mais importantes do nosso setor?" }
  ];

  return (
    <div className="agent-container">
      <Sidebar />
      
      <div className="agent-main">
        <div className="agent-header">
          <div className="header-left">
            <h1>Agente MAWDSLEYS</h1>
            <p className="subtitle">Central de Inteligência Corporativa</p>
            <div className="agent-status">
              <span className="status-indicator active"></span>
              <span className="status-text">Online • Processando dados em tempo real</span>
            </div>
          </div>
          
          <div className="header-right">
            <div className="agent-metrics">
              <div className="metric">
                <div className="metric-value">{documents.length}</div>
                <div className="metric-label">Documentos</div>
              </div>
              <div className="metric">
                <div className="metric-value">{followUps.length}</div>
                <div className="metric-label">Follow-ups</div>
              </div>
              <div className="metric">
                <div className="metric-value">{weeklyAgenda.length}</div>
                <div className="metric-label">Agendamentos</div>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs de Navegação */}
        <div className="agent-tabs">
          <button 
            className={`tab-btn ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            Dashboard
          </button>
          <button 
            className={`tab-btn ${activeTab === "documents" ? "active" : ""}`}
            onClick={() => setActiveTab("documents")}
          >
            Documentos
          </button>
          <button 
            className={`tab-btn ${activeTab === "analysis" ? "active" : ""}`}
            onClick={() => setActiveTab("analysis")}
          >
            Análises
          </button>
          <button 
            className={`tab-btn ${activeTab === "followups" ? "active" : ""}`}
            onClick={() => setActiveTab("followups")}
          >
            Follow-ups
          </button>
          <button 
            className={`tab-btn ${activeTab === "agenda" ? "active" : ""}`}
            onClick={() => setActiveTab("agenda")}
          >
            Pautas
          </button>
          <button 
            className={`tab-btn ${activeTab === "chat" ? "active" : ""}`}
            onClick={() => setActiveTab("chat")}
          >
            Chat
          </button>
        </div>

        {/* Conteúdo das Tabs */}
        <div className="agent-content">
          {loading && (
            <div className="loading-overlay">
              <div className="spinner"></div>
              <p>Agente MAWDSLEYS processando...</p>
            </div>
          )}

          {/* Dashboard */}
          {activeTab === "dashboard" && (
            <div className="dashboard-grid">
              <div className="function-card">
                <div className="function-icon">📊</div>
                <h3>Analisar Documentos</h3>
                <p>Extraia insights automáticos de PDFs, planilhas e apresentações</p>
                <button className="function-btn" onClick={() => setActiveTab("documents")}>
                  Analisar Agora
                </button>
              </div>
              
              <div className="function-card">
                <div className="function-icon">🔄</div>
                <h3>Gerar Follow-ups</h3>
                <p>Crie automaticamente acompanhamentos baseados em prazos e prioridades</p>
                <button className="function-btn" onClick={generateAutoFollowUps}>
                  Gerar Automático
                </button>
              </div>
              
              <div className="function-card">
                <div className="function-icon">📅</div>
                <h3>Construir Pautas</h3>
                <p>Planeje reuniões semanais otimizadas com base nas necessidades</p>
                <button className="function-btn" onClick={generateWeeklyAgenda}>
                  Criar Pauta
                </button>
              </div>
              
              <div className="function-card">
                <div className="function-icon">🔍</div>
                <h3>Consultas Estratégicas</h3>
                <p>Obtenha respostas baseadas em dados internos e externos</p>
                <button className="function-btn" onClick={() => setActiveTab("chat")}>
                  Consultar
                </button>
              </div>
              
              <div className="stats-card wide">
                <h3>Atividade do Agente</h3>
                <div className="activity-list">
                  <div className="activity-item">
                    <span className="activity-time">Agora</span>
                    <span className="activity-text">Analisando tendências de mercado</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">5 min atrás</span>
                    <span className="activity-text">Gerou 3 novos follow-ups</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">15 min atrás</span>
                    <span className="activity-text">Atualizou pauta semanal</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">1 hora atrás</span>
                    <span className="activity-text">Processou relatório financeiro</span>
                  </div>
                </div>
              </div>
              
              <div className="insights-card wide">
                <h3>Insights Detectados</h3>
                <ul className="insights-list">
                  <li>⚠️ <strong>Atenção:</strong> 2 contratos com prazo de renovação próximo</li>
                  <li>📈 <strong>Oportunidade:</strong> Redução de custos em 8% possível</li>
                  <li>🎯 <strong>Meta:</strong> Crescimento de 15% alcançável no próximo trimestre</li>
                  <li>🔄 <strong>Melhoria:</strong> Processo de aprovação pode ser otimizado</li>
                </ul>
              </div>
            </div>
          )}

          {/* Documentos */}
          {activeTab === "documents" && (
            <div className="documents-section">
              <div className="section-header">
                <h2>Documentos para Análise</h2>
                <div className="section-actions">
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx"
                  />
                  <button className="upload-btn" onClick={() => fileInputRef.current.click()}>
                    📤 Upload Documento
                  </button>
                  {uploadedFile && (
                    <div className="uploaded-file">
                      📄 {uploadedFile.name}
                    </div>
                  )}
                </div>
              </div>
              
              <div className="documents-grid">
                {documents.map(doc => (
                  <div key={doc.id} className="document-card">
                    <div className="document-icon">
                      {doc.type === 'pdf' ? '📕' : 
                       doc.type === 'docx' ? '📘' : 
                       doc.type === 'xlsx' ? '📗' : '📙'}
                    </div>
                    <div className="document-info">
                      <h4>{doc.name}</h4>
                      <div className="document-meta">
                        <span>{doc.type.toUpperCase()}</span>
                        <span>{doc.size}</span>
                        <span>{doc.date}</span>
                      </div>
                      <span className={`document-category ${doc.category.toLowerCase()}`}>
                        {doc.category}
                      </span>
                    </div>
                    <button 
                      className="analyze-btn"
                      onClick={() => analyzeDocument(doc)}
                    >
                      Analisar
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Análises */}
          {activeTab === "analysis" && analysisResult && (
            <div className="analysis-section">
              <h2>Resultados da Análise</h2>
              <div className="analysis-result">
                <div className="analysis-header">
                  <span className="analysis-badge">📊 Análise de IA</span>
                  <span className="analysis-date">Gerado em: {new Date().toLocaleDateString('pt-BR')}</span>
                </div>
                <pre className="analysis-content">{analysisResult}</pre>
                <div className="analysis-actions">
                  <button className="action-btn">Exportar PDF</button>
                  <button className="action-btn primary">Gerar Relatório Detalhado</button>
                  <button className="action-btn">Compartilhar</button>
                </div>
              </div>
            </div>
          )}

          {/* Follow-ups */}
          {activeTab === "followups" && (
            <div className="followups-section">
              <div className="section-header">
                <h2>Follow-ups Gerados</h2>
                <button className="generate-btn" onClick={generateAutoFollowUps}>
                  🔄 Gerar Novos
                </button>
              </div>
              
              <div className="followups-grid">
                {followUps.map(followUp => (
                  <div key={followUp.id} className={`followup-card priority-${followUp.priority}`}>
                    <div className="followup-header">
                      <h4>{followUp.title}</h4>
                      <span className={`priority-badge ${followUp.priority}`}>
                        {followUp.priority}
                      </span>
                    </div>
                    <div className="followup-details">
                      <div className="detail">
                        <span className="label">Responsável:</span>
                        <span className="value">{followUp.responsible}</span>
                      </div>
                      <div className="detail">
                        <span className="label">Prazo:</span>
                        <span className="value">{followUp.dueDate}</span>
                      </div>
                      <div className="detail">
                        <span className="label">Status:</span>
                        <span className={`status ${followUp.status}`}>{followUp.status}</span>
                      </div>
                    </div>
                    <div className="followup-actions">
                      <button className="small-btn">Marcar como Concluído</button>
                      <button className="small-btn">Adiar</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Pautas Semanais */}
          {activeTab === "agenda" && (
            <div className="agenda-section">
              <div className="section-header">
                <h2>Pauta da Semana</h2>
                <button className="generate-btn" onClick={generateWeeklyAgenda}>
                  📅 Gerar Nova Pauta
                </button>
              </div>
              
              <div className="calendar-view">
                {['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'].map(day => {
                  const dayEvents = weeklyAgenda.filter(event => event.day === day);
                  
                  return (
                    <div key={day} className="calendar-day">
                      <div className="day-header">
                        <h3>{day}</h3>
                        <span className="event-count">{dayEvents.length} eventos</span>
                      </div>
                      <div className="day-events">
                        {dayEvents.map(event => (
                          <div key={event.id} className={`calendar-event priority-${event.priority}`}>
                            <div className="event-time">{event.time}</div>
                            <div className="event-info">
                              <h4>{event.title}</h4>
                              <div className="event-meta">
                                <span>👥 {event.participants} pessoas</span>
                                <span className={`priority ${event.priority}`}>{event.priority}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Chat Corporativo */}
          {activeTab === "chat" && (
            <div className="chat-section">
              <div className="chat-container">
                <div className="chat-header">
                  <h2>Chat Corporativo</h2>
                  <div className="chat-status">
                    <span className="status-dot"></span>
                    Agente MAWDSLEYS disponível
                  </div>
                </div>
                
                <div className="chat-messages" ref={chatContainerRef}>
                  {chatMessages.map(msg => (
                    <div key={msg.id} className={`message ${msg.sender}`}>
                      <div className="message-avatar">
                        {msg.sender === 'agent' ? '🤖' : '👤'}
                      </div>
                      <div className="message-content">
                        <div className="message-sender">
                          {msg.sender === 'agent' ? 'Agente MAWDSLEYS' : 'Você'}
                        </div>
                        <div className="message-text">{msg.text}</div>
                        <div className="message-time">
                          {new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="quick-actions">
                  {quickActions.map((action, index) => (
                    <button 
                      key={index}
                      className="quick-btn"
                      onClick={() => sendMessage(action.query)}
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
                
                <div className="chat-input-container">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleStrategicQuery()}
                    placeholder="Digite sua consulta estratégica..."
                    className="chat-input"
                  />
                  <button 
                    className="send-btn"
                    onClick={handleStrategicQuery}
                    disabled={!query.trim()}
                  >
                    Enviar
                  </button>
                </div>
              </div>
              
              <div className="chat-sidebar">
                <h3>Consultas Sugeridas</h3>
                <ul className="suggested-queries">
                  <li onClick={() => setQuery("Analise os riscos do próximo trimestre")}>
                    📊 Análise de riscos
                  </li>
                  <li onClick={() => setQuery("Como otimizar nossos processos atuais?")}>
                    ⚡ Otimização de processos
                  </li>
                  <li onClick={() => setQuery("Quais são as oportunidades de crescimento?")}>
                    📈 Oportunidades de crescimento
                  </li>
                  <li onClick={() => setQuery("Analise a concorrência no mercado")}>
                    🎯 Análise da concorrência
                  </li>
                  <li onClick={() => setQuery("Gere insights do último relatório financeiro")}>
                    💰 Insights financeiros
                  </li>
                </ul>
                
                <div className="chat-info">
                  <h4>Capacidades do Agente</h4>
                  <ul>
                    <li>✅ Análise preditiva</li>
                    <li>✅ Processamento de linguagem natural</li>
                    <li>✅ Análise de sentimentos</li>
                    <li>✅ Geração de insights</li>
                    <li>✅ Recomendações estratégicas</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}