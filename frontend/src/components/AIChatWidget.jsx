// src/components/AIChatWidget.jsx - Adaptado ao seu design
import React, { useState, useRef, useEffect } from "react";
import { useAI } from "../contexts/AIContext";
import "./AIChatWidget.css"; // Criar CSS separado

const AIChatWidget = () => {
  const { sendToAI, conversation, isLoading, context } = useAI();
  const [input, setInput] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    await sendToAI(input);
    setInput("");
  };

  // Ações rápidas baseadas nos seus dados
  const quickActions = [
    {
      icon: "📋",
      label: "Follow-ups",
      query: "Mostre meus follow-ups abertos",
    },
    {
      icon: "📅",
      label: "Reuniões",
      query: "Quais reuniões tenho esta semana?",
    },
    {
      icon: "📊",
      label: "KPIs",
      query: "Mostre meus indicadores atuais",
    },
    {
      icon: "🔍",
      label: "Notas",
      query: "Busque em minhas notas",
    },
  ];

  const handleQuickAction = async (query) => {
    await sendToAI(query);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <>
      {/* Botão flutuante estilo WhatsApp */}
      <button
        className={`ai-chat-button ${isOpen ? "active" : ""}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Assistente IA"
      >
        <span className="ai-icon">🤖</span>
        <span className="ai-pulse"></span>
      </button>

      {/* Widget de chat */}
      {isOpen && (
        <div className="ai-chat-widget">
          {/* Cabeçalho */}
          <div className="ai-chat-header">
            <div className="ai-header-info">
              <div className="ai-avatar">🤖</div>
              <div>
                <h4>Assistente MAWDSLEYS</h4>
                <small>
                  {context ? (
                    <>
                      {context.followups?.length || 0} follow-ups •
                      {context.meetings?.length || 0} reuniões
                    </>
                  ) : (
                    "Conectando..."
                  )}
                </small>
              </div>
            </div>
            <button className="ai-close-btn" onClick={() => setIsOpen(false)}>
              ✕
            </button>
          </div>

          {/* Corpo do chat */}
          <div className="ai-chat-body">
            {/* Ações rápidas */}
            {conversation.length === 0 && (
              <div className="ai-welcome">
                <p>Olá! Como posso ajudar você hoje?</p>
                <div className="ai-quick-actions">
                  {quickActions.map((action, idx) => (
                    <button
                      key={idx}
                      className="ai-quick-btn"
                      onClick={() => handleQuickAction(action.query)}
                      disabled={isLoading}
                    >
                      <span className="ai-quick-icon">{action.icon}</span>
                      <span>{action.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Mensagens */}
            <div className="ai-messages">
              {conversation.map((msg, idx) => (
                <div key={idx} className={`ai-message ${msg.role}`}>
                  <div className="ai-message-content">
                    {msg.content}
                    {msg.data && (
                      <div className="ai-message-data">
                        <small>📌 {JSON.stringify(msg.data)}</small>
                      </div>
                    )}
                  </div>
                  <div className="ai-message-time">
                    {msg.timestamp.toLocaleTimeString?.() ||
                      new Date(msg.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="ai-message assistant">
                  <div className="ai-typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form className="ai-input-form" onSubmit={handleSubmit}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Pergunte sobre follow-ups, reuniões, KPIs..."
                disabled={isLoading}
                autoFocus
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="ai-send-btn"
              >
                {isLoading ? "..." : "➤"}
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default AIChatWidget;
