import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";
import "./History.css";

export default function History() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all"); // "all", "aberto", "concluido"
  const [searchTerm, setSearchTerm] = useState("");

  // Corrigindo o useEffect - não usar async diretamente
  useEffect(() => {
    load();
  }, []);

  // Dados de exemplo mais realistas
  const dadosExemplo = [
    {
      id: 1,
      titulo: "Follow-up: Relatório Mensal de Vendas",
      descricao: "Follow-up enviado para a equipe de vendas sobre o relatório mensal. Aguardando feedback sobre os dados de Novembro/2025.",
      data: "2025-11-28",
      hora: "14:30",
      tipo: "followup",
      status: "Aberto",
      responsavel: "Carlos Silva",
      prioridade: "alta",
      tags: ["vendas", "relatório", "mensal"]
    },
    {
      id: 2,
      titulo: "Reunião: Planejamento Q1 2026",
      descricao: "Reunião de alinhamento para o planejamento do primeiro trimestre de 2026. Foram definidas as metas e OKRs.",
      data: "2025-11-25",
      hora: "10:00",
      tipo: "reuniao",
      status: "Concluído",
      responsavel: "Ana Paula",
      prioridade: "media",
      tags: ["planejamento", "reunião", "Q1"]
    },
    {
      id: 3,
      titulo: "Follow-up: Implementação do Novo Sistema",
      descricao: "Acompanhamento da implementação do novo sistema ERP. Foram identificadas 3 pendências técnicas.",
      data: "2025-11-23",
      hora: "16:45",
      tipo: "followup",
      status: "Em andamento",
      responsavel: "TI",
      prioridade: "alta",
      tags: ["sistema", "ERP", "implementação"]
    },
    {
      id: 4,
      titulo: "Aprovação: Contrato com Fornecedor",
      descricao: "Follow-up para aprovação do contrato com novo fornecedor de infraestrutura. Documentação enviada para jurídico.",
      data: "2025-11-20",
      hora: "11:15",
      tipo: "aprovacao",
      status: "Aberto",
      responsavel: "Jurídico",
      prioridade: "alta",
      tags: ["contrato", "fornecedor", "jurídico"]
    },
    {
      id: 5,
      titulo: "Treinamento: Nova Ferramenta de CRM",
      descricao: "Treinamento realizado com a equipe comercial sobre a nova ferramenta de CRM. 85% da equipe participou.",
      data: "2025-11-18",
      hora: "09:00",
      tipo: "treinamento",
      status: "Concluído",
      responsavel: "Marketing",
      prioridade: "baixa",
      tags: ["treinamento", "CRM", "comercial"]
    },
    {
      id: 6,
      titulo: "Follow-up: Orçamento 2026",
      descricao: "Follow-up sobre a elaboração do orçamento para 2026. Aguardando envio das previsões por departamento.",
      data: "2025-11-15",
      hora: "15:30",
      tipo: "followup",
      status: "Aberto",
      responsavel: "Financeiro",
      prioridade: "media",
      tags: ["orçamento", "2026", "financeiro"]
    },
    {
      id: 7,
      titulo: "Manutenção Preventiva",
      descricao: "Manutenção preventiva realizada nos servidores. Todos os sistemas operando normalmente.",
      data: "2025-11-10",
      hora: "22:00",
      tipo: "manutencao",
      status: "Concluído",
      responsavel: "Infraestrutura",
      prioridade: "media",
      tags: ["manutenção", "servidores", "infraestrutura"]
    },
    {
      id: 8,
      titulo: "Follow-up: Campanha de Marketing Digital",
      descricao: "Acompanhamento dos resultados da campanha de marketing digital do último trimestre. ROI de 350% alcançado.",
      data: "2025-11-05",
      hora: "13:20",
      tipo: "followup",
      status: "Concluído",
      responsavel: "Marketing",
      prioridade: "baixa",
      tags: ["marketing", "campanha", "digital"]
    }
  ];

  async function load() {
    try {
      setLoading(true);
      const res = await api.get("/followups/");
      
      // Se a API retornar dados, use-os
      if (res.data && res.data.length > 0) {
        const dadosApi = res.data.map(item => ({
          id: item.id || item._id,
          titulo: item.titulo || item.title || "Sem título",
          descricao: item.descricao || item.description || "",
          data: item.data || item.date || item.createdAt?.split('T')[0] || new Date().toISOString().split('T')[0],
          hora: item.hora || item.time || "00:00",
          tipo: item.tipo || item.type || "followup",
          status: item.status || "Aberto",
          responsavel: item.responsavel || item.responsible || "Não definido",
          prioridade: item.prioridade || item.priority || "media",
          tags: item.tags || []
        }));
        setList(dadosApi);
      } else {
        // Se não houver dados da API, use os dados de exemplo
        setList(dadosExemplo);
      }
    } catch (e) {
      console.error("Erro ao carregar histórico:", e);
      // Em caso de erro, use os dados de exemplo
      setList(dadosExemplo);
    } finally {
      setLoading(false);
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return "Hoje";
    } else if (date.toDateString() === yesterday.toDateString()) {
      return "Ontem";
    } else {
      return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
    }
  };

  const getStatusClass = (status) => {
    switch (status.toLowerCase()) {
      case 'concluído':
      case 'concluido':
        return 'status-completed';
      case 'em andamento':
      case 'em_andamento':
        return 'status-in-progress';
      case 'aberto':
        return 'status-open';
      default:
        return 'status-open';
    }
  };

  const getPriorityClass = (prioridade) => {
    switch (prioridade.toLowerCase()) {
      case 'alta': return 'priority-high';
      case 'media': return 'priority-medium';
      case 'baixa': return 'priority-low';
      default: return 'priority-medium';
    }
  };

  const getTypeIcon = (tipo) => {
    switch (tipo) {
      case 'followup': return '🔄';
      case 'reuniao': return '👥';
      case 'aprovacao': return '✅';
      case 'treinamento': return '📚';
      case 'manutencao': return '🔧';
      default: return '📝';
    }
  };

  // Filtrar itens
  const filteredList = list.filter(item => {
    // Filtro por status
    if (filter !== "all") {
      if (filter === "aberto" && item.status !== "Aberto") return false;
      if (filter === "concluido" && item.status !== "Concluído") return false;
    }
    
    // Filtro por busca
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        item.titulo.toLowerCase().includes(term) ||
        item.descricao.toLowerCase().includes(term) ||
        item.responsavel.toLowerCase().includes(term) ||
        item.tags.some(tag => tag.toLowerCase().includes(term))
      );
    }
    
    return true;
  });

  // Agrupar por data
  const groupedByDate = filteredList.reduce((groups, item) => {
    const date = formatDate(item.data);
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(item);
    return groups;
  }, {});

  const handleRefresh = () => {
    load();
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(filteredList, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `historico-followups-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="history-container">
      <Sidebar />
      
      <div className="history-main">
        <div className="history-header">
          <div className="header-left">
            <h1>Histórico e Follow-ups</h1>
            <p className="subtitle">Acompanhe todo o histórico de atividades e follow-ups</p>
          </div>
          
          <div className="header-actions">
            <button className="btn-refresh" onClick={handleRefresh}>
              <span className="refresh-icon">⟳</span>
              Atualizar
            </button>
            <button className="btn-export" onClick={handleExport}>
              <span className="export-icon">📥</span>
              Exportar
            </button>
          </div>
        </div>

        {/* Filtros */}
        <div className="filters-section">
          <div className="search-box">
            <input 
              type="text" 
              placeholder="Buscar por título, descrição ou responsável..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <span className="search-icon">🔍</span>
          </div>
          
          <div className="filter-tabs">
            <button 
              className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              Todos
            </button>
            <button 
              className={`filter-tab ${filter === 'aberto' ? 'active' : ''}`}
              onClick={() => setFilter('aberto')}
            >
              Abertos
            </button>
            <button 
              className={`filter-tab ${filter === 'concluido' ? 'active' : ''}`}
              onClick={() => setFilter('concluido')}
            >
              Concluídos
            </button>
          </div>
        </div>

        {/* Estatísticas */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{list.length}</div>
            <div className="stat-label">Total de Itens</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{list.filter(i => i.status === 'Aberto').length}</div>
            <div className="stat-label">Abertos</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{list.filter(i => i.status === 'Concluído').length}</div>
            <div className="stat-label">Concluídos</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">
              {list.filter(i => i.prioridade.toLowerCase() === 'alta').length}
            </div>
            <div className="stat-label">Alta Prioridade</div>
          </div>
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Carregando histórico...</p>
          </div>
        ) : filteredList.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📜</div>
            <h3>Nenhum item encontrado</h3>
            <p>Tente alterar os filtros ou criar um novo follow-up.</p>
          </div>
        ) : (
          <div className="history-timeline">
            {Object.entries(groupedByDate).map(([date, items]) => (
              <div key={date} className="timeline-group">
                <div className="timeline-date">
                  <div className="date-line"></div>
                  <div className="date-label">{date}</div>
                  <div className="date-line"></div>
                </div>
                
                <div className="timeline-items">
                  {items.map((item) => (
                    <div key={item.id} className="timeline-card">
                      <div className="timeline-marker">
                        <div className="marker-icon">{getTypeIcon(item.tipo)}</div>
                        <div className="timeline-line"></div>
                      </div>
                      
                      <div className="timeline-content">
                        <div className="card-header">
                          <div className="card-title-row">
                            <h3 className="card-title">{item.titulo}</h3>
                            <div className="card-time">
                              {item.hora}
                            </div>
                          </div>
                          
                          <div className="card-meta">
                            <span className={`status-badge ${getStatusClass(item.status)}`}>
                              {item.status}
                            </span>
                            <span className={`priority-badge ${getPriorityClass(item.prioridade)}`}>
                              {item.prioridade}
                            </span>
                            <span className="responsavel-badge">
                              👤 {item.responsavel}
                            </span>
                          </div>
                        </div>
                        
                        <div className="card-body">
                          <p className="card-description">{item.descricao}</p>
                          
                          {item.tags && item.tags.length > 0 && (
                            <div className="card-tags">
                              {item.tags.map((tag, index) => (
                                <span key={index} className="tag">
                                  #{tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        
                        <div className="card-actions">
                          <button className="btn-view">Ver Detalhes</button>
                          <button className="btn-edit">Editar</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}