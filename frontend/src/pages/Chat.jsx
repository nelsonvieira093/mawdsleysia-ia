// frontend/src/pages/Chat.jsx
import React, { useState, useEffect, useRef } from "react";
import Sidebar from "../components/Sidebar";
import ChatInput from "../components/ChatInput";
import api from "../services/api";
import { useAuth } from "../contexts/AuthContext";
import { getAIContext } from "../services/api";
import ExecutiveBlock from "../components/ExecutiveBlock";

import "./Chat.css";

export default function Chat() {
  const { user } = useAuth();

  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      type: "chat",
      content:
        "👋 Olá! Eu sou o **Agente MAWDSLEYS**.\n\nVocê pode conversar normalmente ou registrar pensamentos executivos (Bullet Journal).",
      timestamp: new Date().toISOString(),
    },
  ]);

  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [aiStatus, setAiStatus] = useState("checking");
  const [aiContext, setAiContext] = useState(null);
  const messagesEndRef = useRef(null);

  // 🔥 modo de operação
  const [mode, setMode] = useState("chat"); // chat | executive

  // =============================
  // STATUS + CONTEXTO DA IA
  // =============================
  useEffect(() => {
    checkAIStatus();
  }, []);

  useEffect(() => {
    if (user?.id) {
      loadAIContext(user.id);
    }
  }, [user?.id]);

  const checkAIStatus = async () => {
    try {
      await api.get("/health"); // ✅ endpoint correto
      setAiStatus("online");
    } catch {
      setAiStatus("offline");
    }
  };

  const loadAIContext = async (userId) => {
    try {
      const context = await getAIContext(userId);
      setAiContext(context);
    } catch (err) {
      console.error("Erro ao carregar contexto IA:", err);
    }
  };

  // =============================
  // AUTO SCROLL
  // =============================
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const formatTime = (dateString) =>
    new Date(dateString).toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    });

  // =============================
  // ENVIO DE MENSAGEM (CHAT / EXECUTIVO)
  // =============================
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isTyping || !user?.id) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      type: mode,
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage("");
    setIsTyping(true);

    try {
      let response;

      // =============================
      // 📘 BULLET JOURNAL (CEO)
      // =============================
      if (mode === "executive") {
        response = await api.post("/api/v1/chat/", {
          message: messageToSend,
          mode: "bullet_journal_ceo",
        });

        const replyText =
          response.data.reply ||
          response.data.response ||
          response.data.message ||
          "Resposta recebida";

        const executiveMessage = {
          id: Date.now() + 1,
          role: "assistant",
          type: "chat",
          content: replyText,
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, executiveMessage]);
      }

      // =============================
      // 💬 CHAT NORMAL
      // =============================
      else {
        response = await api.post("/api/v1/chat/", {
          message: messageToSend,
        });

        const replyText =
          response.data.reply ||
          response.data.response ||
          response.data.message ||
          "Resposta recebida";

        const aiMessage = {
          id: Date.now() + 1,
          role: "assistant",
          type: "chat",
          content: replyText,
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, aiMessage]);
      }
    } catch (err) {
      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        type: "chat",
        content:
          aiStatus === "offline"
            ? "🔌 **IA Offline**\n\nO backend está indisponível."
            : `⚠️ **Erro técnico**\n\n${
                err.response?.data?.detail || err.message
              }`,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
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
        type: "chat",
        content:
          "👋 Nova sessão iniciada.\n\nSelecione Chat ou Bullet Journal Executivo.",
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
            <h1>MAWDSLEYS</h1>
            <div className={`ai-status ${aiStatus}`}>
              <span className="status-dot"></span>
              {aiStatus === "online" ? "IA Online" : "IA Offline"}
            </div>
          </div>

          <div className="header-actions">
            <select value={mode} onChange={(e) => setMode(e.target.value)}>
              <option value="chat">💬 Chat</option>
              <option value="executive">📘 Bullet Journal (CEO)</option>
            </select>

            <button
              className="clear-btn"
              onClick={clearChat}
              disabled={isTyping}
            >
              🗑️ Nova Sessão
            </button>
          </div>
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
                    {message.role === "user" ? "Você" : "MAWDSLEYS"}
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
            <div className="typing-indicator">🤖 Processando...</div>
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
  );
}
