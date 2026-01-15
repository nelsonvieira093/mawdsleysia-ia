//E:\MAWDSLEYS-AGENTE\frontend\src\pages\Deliverables.jsx

import React, { useEffect, useState } from "react";
import api from "../services/api";
import "./Deliverables.css";

// Modal para criar novo entregável
const NewDeliverableModal = ({ isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    responsavel: "",
    prazo: "",
    prioridade: "media",
    status: "pendente",
    progresso: 0,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "progresso" ? parseInt(value) : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newDeliverable = {
      id: Date.now(),
      ...formData,
      dataCriacao: new Date().toISOString().split("T")[0],
    };
    onSave(newDeliverable);
    setFormData({
      title: "",
      description: "",
      responsavel: "",
      prazo: "",
      prioridade: "media",
      status: "pendente",
      progresso: 0,
    });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Novo Entregável</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Título *</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="Título do entregável"
              required
            />
          </div>

          <div className="form-group">
            <label>Descrição</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Descreva o entregável"
              rows="3"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Responsável *</label>
              <select
                name="responsavel"
                value={formData.responsavel}
                onChange={handleChange}
                required
              >
                <option value="">Selecione um responsável</option>
                <option value="Financeiro">Financeiro</option>
                <option value="TI">TI</option>
                <option value="Jurídico">Jurídico</option>
                <option value="Marketing">Marketing</option>
                <option value="Infraestrutura">Infraestrutura</option>
                <option value="Desenvolvimento">Desenvolvimento</option>
                <option value="Design">Design</option>
              </select>
            </div>

            <div className="form-group">
              <label>Prazo *</label>
              <input
                type="date"
                name="prazo"
                value={formData.prazo}
                onChange={handleChange}
                required
                min={new Date().toISOString().split("T")[0]}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Prioridade</label>
              <select
                name="prioridade"
                value={formData.prioridade}
                onChange={handleChange}
              >
                <option value="baixa">Baixa</option>
                <option value="media">Média</option>
                <option value="alta">Alta</option>
              </select>
            </div>

            <div className="form-group">
              <label>Status</label>
              <select
                name="status"
                value={formData.status}
                onChange={handleChange}
              >
                <option value="pendente">Pendente</option>
                <option value="em_andamento">Em Andamento</option>
                <option value="concluido">Concluído</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Progresso ({formData.progresso}%)</label>
            <input
              type="range"
              name="progresso"
              value={formData.progresso}
              onChange={handleChange}
              min="0"
              max="100"
              step="5"
            />
            <div className="range-value">{formData.progresso}%</div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="btn-save">
              Criar Entregável
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Modal para ver detalhes
const DetalhesModal = ({ isOpen, onClose, entregavel, onEditar }) => {
  if (!isOpen || !entregavel) return null;

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  };

  const getStatusText = (status) => {
    switch (status) {
      case "concluido":
        return "Concluído";
      case "em_andamento":
        return "Em Andamento";
      case "pendente":
        return "Pendente";
      default:
        return "Pendente";
    }
  };

  const getPriorityText = (prioridade) => {
    switch (prioridade) {
      case "alta":
        return "Alta";
      case "media":
        return "Média";
      case "baixa":
        return "Baixa";
      default:
        return "Média";
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Detalhes do Entregável</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body-detalhes">
          <h3>{entregavel.title}</h3>

          <div className="detalhes-grid">
            <div className="detalhe-item">
              <span className="detalhe-label">Responsável:</span>
              <span className="detalhe-value">{entregavel.responsavel}</span>
            </div>

            <div className="detalhe-item">
              <span className="detalhe-label">Status:</span>
              <span className={`status-badge ${entregavel.status}`}>
                {getStatusText(entregavel.status)}
              </span>
            </div>

            <div className="detalhe-item">
              <span className="detalhe-label">Prazo:</span>
              <span className="detalhe-value">
                {formatDate(entregavel.prazo)}
              </span>
            </div>

            <div className="detalhe-item">
              <span className="detalhe-label">Prioridade:</span>
              <span className={`priority-badge ${entregavel.prioridade}`}>
                {getPriorityText(entregavel.prioridade)}
              </span>
            </div>
          </div>

          <div className="descricao-container">
            <h4>Descrição</h4>
            <p>{entregavel.description}</p>
          </div>

          <div className="progresso-container">
            <div className="progresso-header">
              <span>Progresso</span>
              <span>{entregavel.progresso}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${entregavel.progresso}%` }}
              ></div>
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Fechar
            </button>
            <button
              type="button"
              className="btn-save"
              onClick={() => {
                onClose();
                onEditar(entregavel);
              }}
            >
              Editar Entregável
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Componente principal
export default function Deliverables() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("todos"); // 'todos', 'pendentes', 'em_andamento', 'concluidos'
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetalhesModalOpen, setIsDetalhesModalOpen] = useState(false);
  const [entregavelSelecionado, setEntregavelSelecionado] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  // Dados de exemplo garantidos
  const dadosExemplo = [
    {
      id: 1,
      title: "Enviar relatório trimestral",
      description: "Relatório financeiro do último trimestre",
      responsavel: "Financeiro",
      prazo: "2025-12-10",
      status: "pendente",
      prioridade: "alta",
      progresso: 30,
      dataCriacao: "2025-11-25",
    },
    {
      id: 2,
      title: "Atualizar documentação do projeto",
      description: "Documentação técnica do sistema",
      responsavel: "TI",
      prazo: "2025-12-15",
      status: "em_andamento",
      prioridade: "media",
      progresso: 65,
      dataCriacao: "2025-11-20",
    },
    {
      id: 3,
      title: "Revisão contratual",
      description: "Revisão dos contratos com fornecedores",
      responsavel: "Jurídico",
      prazo: "2025-12-05",
      status: "concluido",
      prioridade: "alta",
      progresso: 100,
      dataCriacao: "2025-11-15",
    },
    {
      id: 4,
      title: "Planejamento de marketing Q1",
      description: "Planejamento de campanhas para o próximo trimestre",
      responsavel: "Marketing",
      prazo: "2025-12-20",
      status: "pendente",
      prioridade: "media",
      progresso: 10,
      dataCriacao: "2025-11-28",
    },
    {
      id: 5,
      title: "Manutenção de infraestrutura",
      description: "Atualização dos servidores e rede",
      responsavel: "Infraestrutura",
      prazo: "2025-12-12",
      status: "em_andamento",
      prioridade: "alta",
      progresso: 45,
      dataCriacao: "2025-11-22",
    },
  ];

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    try {
      const res = await api.get("/followups/");
      console.log("API Response:", res.data);

      // Se a API retornar dados, use-os
      if (res.data && res.data.length > 0) {
        // Normalizar os dados da API para o formato esperado
        const dadosApi = res.data.map((item) => ({
          id: item.id || item._id || Date.now(),
          title: item.title || item.nome || "Sem título",
          description: item.description || item.descricao || "",
          responsavel: item.responsavel || item.responsible || "Não definido",
          prazo:
            item.prazo ||
            item.due_date ||
            new Date().toISOString().split("T")[0],
          status: item.status || "pendente",
          prioridade: item.prioridade || item.priority || "media",
          progresso: item.progresso || item.progress || 0,
          dataCriacao:
            item.dataCriacao ||
            item.createdAt ||
            new Date().toISOString().split("T")[0],
        }));
        setItems(dadosApi);
      } else {
        // Se não houver dados da API, use os dados de exemplo
        setItems(dadosExemplo);
      }
    } catch (e) {
      console.error("Erro ao carregar entregáveis:", e);
      // Em caso de erro, use os dados de exemplo
      setItems(dadosExemplo);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("pt-BR");
    } catch (e) {
      return dateString;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case "concluido":
        return "status-completed";
      case "em_andamento":
        return "status-in-progress";
      case "pendente":
        return "status-pending";
      default:
        return "status-pending";
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case "concluido":
        return "Concluído";
      case "em_andamento":
        return "Em Andamento";
      case "pendente":
        return "Pendente";
      default:
        return "Pendente";
    }
  };

  const getPriorityClass = (prioridade) => {
    switch (prioridade) {
      case "alta":
        return "priority-high";
      case "media":
        return "priority-medium";
      case "baixa":
        return "priority-low";
      default:
        return "priority-medium";
    }
  };

  const getPriorityText = (prioridade) => {
    switch (prioridade) {
      case "alta":
        return "Alta";
      case "media":
        return "Média";
      case "baixa":
        return "Baixa";
      default:
        return "Média";
    }
  };

  // Filtrar itens pela aba ativa e busca
  const filteredItems = items.filter((item) => {
    // Filtro por status
    if (activeTab === "pendentes" && item.status !== "pendente") return false;
    if (activeTab === "em_andamento" && item.status !== "em_andamento")
      return false;
    if (activeTab === "concluidos" && item.status !== "concluido") return false;

    // Filtro por busca
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        item.title.toLowerCase().includes(term) ||
        item.description.toLowerCase().includes(term) ||
        item.responsavel.toLowerCase().includes(term)
      );
    }

    return true;
  });

  const handleAddDeliverable = (newDeliverable) => {
    setItems((prev) => [...prev, newDeliverable]);
  };

  const handleUpdateDeliverable = (updatedDeliverable) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === updatedDeliverable.id ? updatedDeliverable : item
      )
    );
  };

  const handleDeleteDeliverable = (id) => {
    if (window.confirm("Tem certeza que deseja excluir este entregável?")) {
      setItems((prev) => prev.filter((item) => item.id !== id));
    }
  };

  const handleVerDetalhes = (item) => {
    setEntregavelSelecionado(item);
    setIsDetalhesModalOpen(true);
  };

  const handleEditar = (item) => {
    setEntregavelSelecionado(item);
    setIsModalOpen(true);
  };

  return (
    <div className="deliverables-container">
      <div className="deliverables-header">
        <div className="header-left">
          <h1>Entregáveis</h1>
          <p className="subtitle">Acompanhe os entregáveis por diretoria</p>
        </div>

        <div className="header-right">
          <div className="stats">
            <div className="stat-item">
              <span className="stat-number">{items.length}</span>
              <span className="stat-label">Total</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">
                {items.filter((i) => i.status === "concluido").length}
              </span>
              <span className="stat-label">Concluídos</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">
                {items.filter((i) => i.status === "pendente").length}
              </span>
              <span className="stat-label">Pendentes</span>
            </div>
          </div>

          <button
            className="btn-new-deliverable"
            onClick={() => setIsModalOpen(true)}
          >
            <span className="plus-icon">+</span>
            Novo Entregável
          </button>
        </div>
      </div>

      {/* Abas */}
      <div className="tabs-container">
        <button
          className={`tab-btn ${activeTab === "todos" ? "active" : ""}`}
          onClick={() => setActiveTab("todos")}
        >
          Todos
        </button>
        <button
          className={`tab-btn ${activeTab === "pendentes" ? "active" : ""}`}
          onClick={() => setActiveTab("pendentes")}
        >
          Pendentes
        </button>
        <button
          className={`tab-btn ${activeTab === "em_andamento" ? "active" : ""}`}
          onClick={() => setActiveTab("em_andamento")}
        >
          Em Andamento
        </button>
        <button
          className={`tab-btn ${activeTab === "concluidos" ? "active" : ""}`}
          onClick={() => setActiveTab("concluidos")}
        >
          Concluídos
        </button>
      </div>

      {/* Filtro de busca */}
      <div className="filters-container">
        <div className="search-box">
          <input
            type="text"
            placeholder="Buscar por título, descrição ou responsável..."
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button className="search-btn">🔍</button>
        </div>
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Carregando entregáveis...</p>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📦</div>
          <h3>Nenhum entregável encontrado</h3>
          <p>Tente alterar os filtros ou criar um novo entregável.</p>
          <button
            className="btn-new-deliverable"
            onClick={() => setIsModalOpen(true)}
            style={{ marginTop: "20px" }}
          >
            <span className="plus-icon">+</span>
            Criar Primeiro Entregável
          </button>
        </div>
      ) : (
        <div className="deliverables-grid">
          {filteredItems.map((item) => (
            <div key={item.id} className="deliverable-card">
              <div className="card-header">
                <div className="card-top">
                  <span
                    className={`priority-badge ${getPriorityClass(
                      item.prioridade
                    )}`}
                  >
                    {getPriorityText(item.prioridade)}
                  </span>
                  <div className="card-actions">
                    <button
                      className="icon-btn"
                      title="Editar"
                      onClick={() => handleEditar(item)}
                    >
                      ✏️
                    </button>
                    <button
                      className="icon-btn"
                      title="Excluir"
                      onClick={() => handleDeleteDeliverable(item.id)}
                    >
                      🗑️
                    </button>
                  </div>
                </div>

                <h3 className="deliverable-title">{item.title}</h3>

                <div className="deliverable-responsavel">
                  <span className="label">Responsável:</span>
                  <span className="value">{item.responsavel}</span>
                </div>
              </div>

              <div className="card-body">
                {item.description && (
                  <p className="deliverable-description">{item.description}</p>
                )}

                <div className="deliverable-details">
                  <div className="detail-item">
                    <span className="label">Prazo:</span>
                    <span className="value">{formatDate(item.prazo)}</span>
                  </div>

                  <div className="progress-container">
                    <div className="progress-label">
                      <span>Progresso</span>
                      <span>{item.progresso || 0}%</span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${item.progresso || 0}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card-footer">
                <div className={`status-badge ${getStatusClass(item.status)}`}>
                  {getStatusText(item.status)}
                </div>

                <div className="footer-actions">
                  <button
                    className="btn-view"
                    onClick={() => handleVerDetalhes(item)}
                  >
                    Ver Detalhes
                  </button>
                  <button
                    className="btn-update"
                    onClick={() => handleEditar(item)}
                  >
                    Atualizar
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal para criar/editar entregável */}
      <NewDeliverableModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEntregavelSelecionado(null);
        }}
        onSave={(deliverable) => {
          if (entregavelSelecionado) {
            handleUpdateDeliverable({
              ...entregavelSelecionado,
              ...deliverable,
            });
          } else {
            handleAddDeliverable(deliverable);
          }
        }}
      />

      {/* Modal para ver detalhes */}
      <DetalhesModal
        isOpen={isDetalhesModalOpen}
        onClose={() => {
          setIsDetalhesModalOpen(false);
          setEntregavelSelecionado(null);
        }}
        entregavel={entregavelSelecionado}
        onEditar={(item) => {
          setIsDetalhesModalOpen(false);
          handleEditar(item);
        }}
      />
    </div>
  );
}
