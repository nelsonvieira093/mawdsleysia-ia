// E:\MAWDSLEYS-AGENTE\frontend\src\pages\Chat.jsx

import React, { useState, useEffect, useRef } from "react";
import Sidebar from "../components/Sidebar";
import ChatInput from "../components/ChatInput";
import api from "../services/api";
import "./Chat.css";

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      content:
        "👋 Olá! Eu sou o **Agente MAWDSLEYS**, seu assistente de inteligência corporativa. Posso ajudar com:\n\n• 📊 Análise de documentos\n• 🔄 Geração de follow-ups\n• 📅 Planejamento de pautas\n• 🔍 Consultas estratégicas\n\nComo posso ajudá-lo hoje?",
      timestamp: new Date().toISOString(),
    },
  ]);

  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [aiStatus, setAiStatus] = useState("checking");
  const messagesEndRef = useRef(null);

  // =============================
  // STATUS DA IA
  // =============================
  useEffect(() => {
    checkAIStatus();
  }, []);

  const checkAIStatus = async () => {
    try {
      const response = await api.get("/api/v1/chat/health");
      setAiStatus(response.status === 200 ? "online" : "offline");
    } catch {
      setAiStatus("offline");
    }
  };

  // =============================
  // AUTO SCROLL
  // =============================
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const suggestedTopics = [
    "Analisar relatório financeiro",
    "Gerar follow-ups automáticos",
    "Criar pauta semanal",
    "Consultar base de conhecimento",
    "Analisar tendências de mercado",
  ];

  // =============================
  // ENVIO DE MENSAGEM (CHAT REAL)
  // =============================
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isTyping) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);

    const messageToSend = inputMessage;
    setInputMessage("");
    setIsTyping(true);

    try {
      // ✅ CORREÇÃO DEFINITIVA: barra final
      const response = await api.post("/api/v1/chat/", {
        message: messageToSend,
      });

      const aiMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: response.data.reply,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          content:
            "🔧 **Ops!** Estou com dificuldades técnicas no momento.\n\nTente novamente em instantes.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickTopic = (topic) => {
    setInputMessage(topic);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        role: "assistant",
        content:
          "👋 Olá! Eu sou o **Agente MAWDSLEYS**, seu assistente de inteligência corporativa. Como posso ajudá-lo hoje?",
        timestamp: new Date().toISOString(),
      },
    ]);
  };

  // =============================
  // RENDER
  // =============================
  return (
    <div className="chat-page-container">
      <Sidebar />

      <div className="chat-main-area">
        <div className="chat-header">
          <div className="header-left">
            <h1>Chat MAWDSLEYS</h1>
            <div className={`ai-status ${aiStatus}`}>
              <span className="status-dot"></span>
              {aiStatus === "online" ? "IA Online" : "IA Offline"}
            </div>
          </div>

          <button className="clear-btn" onClick={clearChat} disabled={isTyping}>
            🗑️ Nova Conversa
          </button>
        </div>

        <div className="chat-content">
          <div className="suggestions-section">
            {suggestedTopics.map((topic, index) => (
              <button
                key={index}
                className="suggestion-btn"
                onClick={() => handleQuickTopic(topic)}
              >
                {topic}
              </button>
            ))}
          </div>

          <div className="messages-container">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message-wrapper ${
                  message.role === "user" ? "user-message" : "bot-message"
                }`}
              >
                <div className="message-avatar">
                  {message.role === "user" ? "👤" : "🤖"}
                </div>
                <div className="message-content">
                  <div className="message-header">
                    <strong>
                      {message.role === "user" ? "Você" : "Agente MAWDSLEYS"}
                    </strong>
                    <span>{formatTime(message.timestamp)}</span>
                  </div>
                  <div className="message-text">
                    {message.content.split("\n").map((line, i) => (
                      <div key={i}>{line}</div>
                    ))}
                  </div>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="typing-indicator">🤖 Digitando...</div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <ChatInput
            value={inputMessage}
            onChange={setInputMessage}
            onSend={handleSendMessage}
            onKeyPress={handleKeyPress}
            isTyping={isTyping}
            aiStatus={aiStatus}
          />
        </div>
      </div>
    </div>
  );
}
