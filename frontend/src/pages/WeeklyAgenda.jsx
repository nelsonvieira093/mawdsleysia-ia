//E: \MAWDSLEYS - AGENTE\frontend\src\pages\WeeklyAgenda.jsx
import React, { useEffect, useState } from "react";
import api from "../services/api";
import "./WeeklyAgenda.css";

// MODAL DE DETALHES DA PAUTA
const MeetingDetailsModal = ({ meeting, isOpen, onClose }) => {
  if (!isOpen || !meeting) return null;

  const formatFullDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("pt-BR", {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (error) {
      return dateString;
    }
  };

  const getStatusText = (status) => {
    const textMap = {
      confirmado: "Confirmada",
      pendente: "Pendente",
      cancelado: "Cancelada",
    };
    return textMap[status?.toLowerCase()] || "Pendente";
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="meeting-details-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div className="modal-title">
            <h2>{meeting.title}</h2>
            <span className={`meeting-status ${meeting.status}`}>
              {getStatusText(meeting.status)}
            </span>
          </div>
          <button className="close-modal" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="details-grid">
            <div className="detail-item">
              <div className="detail-label">
                <span className="icon">📅</span>
                <span>Data e Hora</span>
              </div>
              <div className="detail-value">{formatFullDate(meeting.date)}</div>
            </div>

            <div className="detail-item">
              <div className="detail-label">
                <span className="icon">👤</span>
                <span>Responsável</span>
              </div>
              <div className="detail-value">{meeting.owner}</div>
            </div>

            <div className="detail-item">
              <div className="detail-label">
                <span className="icon">👥</span>
                <span>Participantes</span>
              </div>
              <div className="detail-value">
                {meeting.participants || "Não especificado"}
              </div>
            </div>

            <div className="detail-item">
              <div className="detail-label">
                <span className="icon">📍</span>
                <span>Local</span>
              </div>
              <div className="detail-value">
                {meeting.location || "A definir"}
              </div>
            </div>
          </div>

          {meeting.description && (
            <div className="description-section">
              <h3>
                <span className="icon">📝</span>
                Descrição
              </h3>
              <p>{meeting.description}</p>
            </div>
          )}

          <div className="agenda-section">
            <h3>
              <span className="icon">📋</span>
              Pauta da Reunião
            </h3>
            {meeting.agendaItems ? (
              <ul className="agenda-list">
                {meeting.agendaItems.map((item, index) => (
                  <li key={index}>
                    <span className="agenda-number">{index + 1}.</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="no-agenda">
                <p>Nenhum item de pauta definido ainda.</p>
                <button className="btn-add-agenda">
                  <span className="plus-icon">+</span>
                  Adicionar Itens
                </button>
              </div>
            )}
          </div>

          <div className="attachments-section">
            <h3>
              <span className="icon">📎</span>
              Anexos
            </h3>
            {meeting.attachments ? (
              <div className="attachments-list">
                {meeting.attachments.map((attachment, index) => (
                  <div key={index} className="attachment-item">
                    <span className="attachment-icon">📄</span>
                    <span className="attachment-name">{attachment.name}</span>
                    <button className="btn-download">↓</button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-attachments">Nenhum anexo disponível.</p>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Fechar
          </button>
          <div className="footer-actions">
            <button className="btn-edit">
              <span className="icon">✏️</span>
              Editar Pauta
            </button>
            <button className="btn-primary">
              <span className="icon">📧</span>
              Enviar Convites
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// COMPONENTE MEETING CARD (atualizado)
const MeetingCard = ({ meeting, onEdit, onDelete, onViewDetails }) => {
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("pt-BR", {
        weekday: "short",
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (error) {
      return dateString;
    }
  };

  const getStatusClass = (status) => {
    const statusMap = {
      confirmado: "status-confirmed",
      pendente: "status-pending",
      cancelado: "status-cancelled",
    };
    return statusMap[status?.toLowerCase()] || "status-pending";
  };

  const getStatusText = (status) => {
    const textMap = {
      confirmado: "CONFIRMADO",
      pendente: "PENDENTE",
      cancelado: "CANCELADO",
    };
    return textMap[status?.toLowerCase()] || "PENDENTE";
  };

  return (
    <div className="meeting-card">
      <div className="card-top">
        <div className={`status-indicator ${getStatusClass(meeting.status)}`}>
          {getStatusText(meeting.status)}
        </div>
        <div className="card-actions-menu">
          <button
            className="icon-btn"
            onClick={() => onEdit(meeting)}
            title="Editar"
          >
            ✏️
          </button>
          <button
            className="icon-btn"
            onClick={() => onDelete(meeting.id)}
            title="Excluir"
          >
            🗑️
          </button>
        </div>
      </div>

      <div className="card-content">
        <h3 className="meeting-title">{meeting.title}</h3>

        <div className="meeting-info">
          <div className="info-item">
            <span className="icon">📅</span>
            <span>{formatDate(meeting.date)}</span>
          </div>
          <div className="info-item">
            <span className="icon">👤</span>
            <span>{meeting.owner}</span>
          </div>
          {meeting.participants && (
            <div className="info-item">
              <span className="icon">👥</span>
              <span>{meeting.participants} participantes</span>
            </div>
          )}
        </div>

        {meeting.description && (
          <p className="meeting-description">{meeting.description}</p>
        )}
      </div>

      <div className="card-footer">
        <button
          className="btn-view-agenda"
          onClick={() => onViewDetails(meeting)}
        >
          <span className="eye-icon">👁️</span>
          Ver Pauta Completa
        </button>
      </div>
    </div>
  );
};

// MODAL PARA CRIAR/EDITAR PAUTA (mantido da versão anterior)
const NewMeetingModal = ({ isOpen, onClose, onSave, initialData }) => {
  const [formData, setFormData] = useState({
    title: "",
    date: "",
    time: "",
    owner: "",
    description: "",
    participants: 1,
    status: "pendente",
    location: "",
    agendaItems: [],
    attachments: [],
  });

  useEffect(() => {
    if (initialData) {
      // Se estiver editando, preenche o formulário com os dados existentes
      const date = initialData.date ? initialData.date.split("T")[0] : "";
      const time = initialData.date
        ? initialData.date.split("T")[1]?.substring(0, 5)
        : "";

      setFormData({
        title: initialData.title || "",
        date: date,
        time: time,
        owner: initialData.owner || "",
        description: initialData.description || "",
        participants: initialData.participants || 1,
        status: initialData.status || "pendente",
        location: initialData.location || "",
        agendaItems: initialData.agendaItems || [],
        attachments: initialData.attachments || [],
      });
    } else {
      // Se for nova pauta, reseta o formulário
      setFormData({
        title: "",
        date: "",
        time: "",
        owner: "",
        description: "",
        participants: 1,
        status: "pendente",
        location: "",
        agendaItems: [],
        attachments: [],
      });
    }
  }, [initialData, isOpen]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Formatar data e hora
    const dateTime = `${formData.date}T${formData.time}:00`;

    const meetingData = {
      id: initialData ? initialData.id : Date.now(),
      title: formData.title,
      date: dateTime,
      owner: formData.owner,
      status: formData.status,
      description: formData.description,
      participants: parseInt(formData.participants),
      location: formData.location,
      agendaItems: formData.agendaItems,
      attachments: formData.attachments,
    };

    onSave(meetingData);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{initialData ? "Editar Pauta" : "Nova Pauta"}</h2>
          <button className="close-modal" onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Título da Reunião *</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="Ex: Reunião de Planejamento"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Data *</label>
              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Hora *</label>
              <input
                type="time"
                name="time"
                value={formData.time}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Responsável *</label>
            <input
              type="text"
              name="owner"
              value={formData.owner}
              onChange={handleChange}
              placeholder="Ex: Gerente João"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Participantes</label>
              <input
                type="number"
                name="participants"
                value={formData.participants}
                onChange={handleChange}
                min="1"
                max="50"
              />
            </div>

            <div className="form-group">
              <label>Status</label>
              <select
                name="status"
                value={formData.status}
                onChange={handleChange}
              >
                <option value="pendente">Pendente</option>
                <option value="confirmado">Confirmado</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Local</label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="Ex: Sala de Reuniões 1"
            />
          </div>

          <div className="form-group">
            <label>Descrição</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Descreva os objetivos desta reunião..."
              rows="3"
            />
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="btn-primary">
              {initialData ? "Salvar Alterações" : "Criar Pauta"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// COMPONENTE PRINCIPAL
export default function WeeklyAgenda() {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isNewMeetingModalOpen, setIsNewMeetingModalOpen] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [editingMeeting, setEditingMeeting] = useState(null);
  const [selectedMeeting, setSelectedMeeting] = useState(null);

  useEffect(() => {
    loadMeetings();
  }, []);

  const loadMeetings = async () => {
    try {
      const res = await api.get("api/agenda");
      setMeetings(res.data?.items || []);
    } catch {
      // Dados de exemplo
      setMeetings([
        {
          id: 1,
          title: "Reunião de Operações",
          date: "2025-12-06T10:00:00",
          owner: "Diretor A",
          status: "pendente",
          description:
            "Revisão das operações semanais e definição de metas para o próximo período.",
          participants: 5,
          location: "Sala de Reuniões Principal",
          agendaItems: [
            "Análise das métricas semanais",
            "Definição de novas metas",
            "Distribuição de tarefas",
            "Próximos passos",
          ],
          attachments: [
            { name: "Métricas_Semanais.pdf", url: "#" },
            { name: "Apresentação_Resultados.pptx", url: "#" },
          ],
        },
        {
          id: 2,
          title: "Análise de Métricas",
          date: "2025-12-07T14:30:00",
          owner: "Gerente B",
          status: "confirmado",
          description:
            "Análise detalhada dos KPIs do trimestre e ajustes estratégicos.",
          participants: 3,
          location: "Sala de Videoconferência",
          agendaItems: [
            "Apresentação dos resultados",
            "Análise comparativa com trimestre anterior",
            "Definição de ajustes necessários",
          ],
        },
        {
          id: 3,
          title: "Planejamento Trimestral",
          date: "2025-12-08T09:00:00",
          owner: "CEO",
          status: "pendente",
          description:
            "Planejamento estratégico para o próximo trimestre com foco em expansão.",
          participants: 8,
          location: "Auditório",
          agendaItems: [
            "Revisão do plano atual",
            "Definição de novas metas trimestrais",
            "Alocação de recursos",
            "Cronograma de implementação",
          ],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddMeeting = (newMeeting) => {
    setMeetings((prev) => [...prev, newMeeting]);
  };

  const handleEditMeeting = (updatedMeeting) => {
    setMeetings((prev) =>
      prev.map((meeting) =>
        meeting.id === updatedMeeting.id ? updatedMeeting : meeting
      )
    );
    setEditingMeeting(null);
    setIsNewMeetingModalOpen(false);
  };

  const handleDeleteMeeting = (id) => {
    if (window.confirm("Tem certeza que deseja excluir esta pauta?")) {
      setMeetings((prev) => prev.filter((meeting) => meeting.id !== id));
    }
  };

  const openEditModal = (meeting) => {
    setEditingMeeting(meeting);
    setIsNewMeetingModalOpen(true);
  };

  const openDetailsModal = (meeting) => {
    setSelectedMeeting(meeting);
    setIsDetailsModalOpen(true);
  };

  const handleSaveMeeting = (meetingData) => {
    if (editingMeeting) {
      handleEditMeeting(meetingData);
    } else {
      handleAddMeeting(meetingData);
    }
  };

  const confirmedMeetings = meetings.filter((m) => m.status === "confirmado");
  const pendingMeetings = meetings.filter((m) => m.status === "pendente");

  return (
    <div className="weekly-agenda-container">
      <div className="agenda-header">
        <div className="header-left">
          <h1>Pautas da Semana</h1>
          <div className="header-stats">
            <span className="stat-item">
              <span className="stat-number">{meetings.length}</span>
              <span className="stat-label">Total</span>
            </span>
            <span className="stat-item">
              <span className="stat-number">{confirmedMeetings.length}</span>
              <span className="stat-label">Confirmadas</span>
            </span>
            <span className="stat-item">
              <span className="stat-number">{pendingMeetings.length}</span>
              <span className="stat-label">Pendentes</span>
            </span>
          </div>
        </div>

        <button
          className="btn-new-meeting"
          onClick={() => {
            setEditingMeeting(null);
            setIsNewMeetingModalOpen(true);
          }}
        >
          <span className="plus-icon">+</span>
          Nova Pauta
        </button>
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Carregando pautas...</p>
        </div>
      ) : (
        <>
          {confirmedMeetings.length > 0 && (
            <div className="agenda-section">
              <div className="section-header">
                <h2>
                  <span className="section-icon">✅</span>
                  Confirmadas
                </h2>
                <span className="section-count">
                  {confirmedMeetings.length}
                </span>
              </div>

              <div className="meetings-grid">
                {confirmedMeetings.map((meeting) => (
                  <MeetingCard
                    key={meeting.id}
                    meeting={meeting}
                    onEdit={openEditModal}
                    onDelete={handleDeleteMeeting}
                    onViewDetails={openDetailsModal}
                  />
                ))}
              </div>
            </div>
          )}

          {pendingMeetings.length > 0 && (
            <div className="agenda-section">
              <div className="section-header">
                <h2>
                  <span className="section-icon">⏳</span>
                  Pendentes
                </h2>
                <span className="section-count">{pendingMeetings.length}</span>
              </div>

              <div className="meetings-grid">
                {pendingMeetings.map((meeting) => (
                  <MeetingCard
                    key={meeting.id}
                    meeting={meeting}
                    onEdit={openEditModal}
                    onDelete={handleDeleteMeeting}
                    onViewDetails={openDetailsModal}
                  />
                ))}
              </div>
            </div>
          )}

          {meetings.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📅</div>
              <h3>Nenhuma pauta esta semana</h3>
              <p>Comece criando sua primeira pauta de reunião.</p>
              <button
                className="btn-new-meeting"
                onClick={() => setIsNewMeetingModalOpen(true)}
              >
                <span className="plus-icon">+</span>
                Criar Primeira Pauta
              </button>
            </div>
          )}
        </>
      )}

      {/* Modal para criar/editar pauta */}
      <NewMeetingModal
        isOpen={isNewMeetingModalOpen}
        onClose={() => {
          setIsNewMeetingModalOpen(false);
          setEditingMeeting(null);
        }}
        onSave={handleSaveMeeting}
        initialData={editingMeeting}
      />

      {/* Modal para ver detalhes da pauta */}
      <MeetingDetailsModal
        meeting={selectedMeeting}
        isOpen={isDetailsModalOpen}
        onClose={() => setIsDetailsModalOpen(false)}
      />
    </div>
  );
}
