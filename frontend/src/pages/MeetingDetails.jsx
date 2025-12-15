import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import "./MeetingDetails.css";

export default function MeetingDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [meeting, setMeeting] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMeeting();
  }, [id]);

  async function loadMeeting() {
    try {
      // Aqui você faria uma chamada para a API para buscar os detalhes da pauta pelo id
      // Como exemplo, vamos simular uma busca nos dados existentes
      const res = await api.get(`/agenda/${id}`);
      setMeeting(res.data);
    } catch (error) {
      console.error("Erro ao carregar detalhes da pauta:", error);
      // Se não encontrar, redireciona de volta para a agenda
      navigate("/agenda");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Carregando detalhes da pauta...</p>
      </div>
    );
  }

  if (!meeting) {
    return (
      <div className="empty-state">
        <h3>Pauta não encontrada</h3>
        <button onClick={() => navigate("/agenda")}>Voltar para Agenda</button>
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="meeting-details-container">
      <div className="details-header">
        <button className="btn-back" onClick={() => navigate("/agenda")}>
          ← Voltar
        </button>
        <h1>{meeting.title}</h1>
        <div className={`status-badge ${meeting.status}`}>
          {meeting.status === 'confirmado' ? 'CONFIRMADO' : 'PENDENTE'}
        </div>
      </div>

      <div className="details-content">
        <div className="details-card">
          <h3>📅 Data e Hora</h3>
          <p>{formatDate(meeting.date)}</p>
        </div>

        <div className="details-card">
          <h3>👤 Responsável</h3>
          <p>{meeting.owner}</p>
        </div>

        <div className="details-card">
          <h3>👥 Participantes</h3>
          <p>{meeting.participants || 'Não informado'}</p>
        </div>

        <div className="details-card full-width">
          <h3>📝 Descrição</h3>
          <p>{meeting.description || 'Sem descrição.'}</p>
        </div>

        <div className="details-card full-width">
          <h3>📋 Pauta da Reunião</h3>
          <div className="agenda-items">
            {meeting.agendaItems ? (
              <ul>
                {meeting.agendaItems.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            ) : (
              <p>Nenhum item de pauta definido.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}