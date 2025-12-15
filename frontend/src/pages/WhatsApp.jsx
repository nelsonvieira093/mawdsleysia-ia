// frontend/src/pages/WhatsApp.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";

import ConversationList from "../components/whatsapp/ConversationList";
import ChatWindow from "../components/whatsapp/ChatWindow";
import StatusBar from "../components/whatsapp/StatusBar";

import { listConversations, getWebhookStatus } from "../services/whatsapp";

import "./WhatsApp.css";

export default function WhatsApp() {
  const [conversations, setConversations] = useState([]);
  const [active, setActive] = useState(null);
  const [webhook, setWebhook] = useState({ status: "loading" });

  const [loadingConversations, setLoadingConversations] = useState(true);

  // =======================================================
  // Carrega conversas + status do webhook ao abrir a página
  // =======================================================
  useEffect(() => {
    loadConversations();
    loadWebhookStatus();
  }, []);

  async function loadConversations() {
    try {
      setLoadingConversations(true);
      const list = await listConversations();
      setConversations(list || []);
      if (list && list.length > 0) setActive(list[0].id);
    } catch (err) {
      console.error("Erro ao carregar conversas:", err);
    } finally {
      setLoadingConversations(false);
    }
  }

  async function loadWebhookStatus() {
    try {
      const status = await getWebhookStatus();
      setWebhook(status || { status: "offline" });
    } catch (err) {
      console.error("Erro no webhook:", err);
      setWebhook({ status: "offline" });
    }
  }

  return (
    <div className="page-with-sidebar">
      <Sidebar />

      <main className="whatsapp-page">
        {/* Título */}
        <div className="wh-header">
          <h1 className="page-title">WhatsApp Corporativo</h1>
        </div>

        {/* Status do Webhook */}
        <StatusBar data={webhook} />

        {/* Painel principal */}
        <div className="wa-panel">
          
          {/* LISTA DE CONVERSAS */}
          <div className="wa-left">
            {loadingConversations ? (
              <div className="wa-loading">Carregando conversas...</div>
            ) : conversations.length === 0 ? (
              <div className="wa-empty">
                Nenhuma conversa recebida ainda.
                <br />
                Envie uma mensagem para o número conectado ao webhook.
              </div>
            ) : (
              <ConversationList
                conversations={conversations}
                active={active}
                onSelect={setActive}
              />
            )}
          </div>

          {/* JANELA DE CHAT */}
          <div className="wa-right">
            {active ? (
              <ChatWindow conversationId={active} />
            ) : (
              <div className="wa-no-chat">
                Selecione uma conversa à esquerda
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}
