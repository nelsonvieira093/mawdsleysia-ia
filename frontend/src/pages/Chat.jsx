// frontend/src/pages/Chat.jsx
import React, { useState, useEffect, useRef } from "react";
import Sidebar from "../components/Sidebar";
import ChatInput from "../components/ChatInput";
import api from "../services/api";
import { useAuth } from "../contexts/AuthContext";
import { getAIContext } from "../services/api";
import "./Chat.css";

export default function Chat() {
  const { user } = useAuth();

  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      content:
        "👋 Olá! Eu sou o **Agente MAWDSLEYS**, seu assistente de inteligência corporativa.\n\nTenho acesso ao seu **dashboard, follow-ups, pautas, documentos e KPIs**.\n\nComo posso ajudar?",
      timestamp: new Date().toISOString(),
    },
  ]);

  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [aiStatus, setAiStatus] = useState("checking");
  const [aiContext, setAiContext] = useState(null);
  const messagesEndRef = useRef(null);

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
      await api.get("/openapi.json");
      setAiStatus("online");
      console.log("✅ Backend conectado");
    } catch {
      setAiStatus("offline");
      console.log("❌ Backend offline");
    }
  };

  const loadAIContext = async (userId) => {
    try {
      const context = await getAIContext(userId);
      setAiContext(context);
      console.log("🧠 Contexto IA carregado:", context);
    } catch (err) {
      console.error("❌ Erro ao carregar contexto IA:", err);
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

  // =============================
  // ENVIO DE MENSAGEM (CORREÇÃO CIRÚRGICA)
  // =============================
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isTyping || !user?.id) return;

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
      // 🔥 CORREÇÃO 1: Endpoint correto com barra final
      // 🔥 CORREÇÃO 2: Payload simplificado (o backend atual não usa context)
      const response = await api.post("/api/v1/chat/", {
        message: messageToSend, // Apenas message, não user_id nem context
      });

      console.log("📦 Resposta completa:", response.data); // DEBUG

      // 🔥 CORREÇÃO 3: Tratamento correto da resposta
      // Backend retorna: {reply: "texto", status: "success", timestamp: "..."}
      const replyText =
        response.data.reply ||
        response.data.response ||
        response.data.message ||
        "Resposta recebida";

      console.log("📝 Texto extraído:", replyText);

      const aiMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: replyText,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error("❌ Erro no chat:", err);
      console.error("❌ Detalhes do erro:", {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message,
      });

      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          aiStatus === "offline"
            ? "🔌 **IA Offline**\n\nO backend está indisponível no momento."
            : `⚠️ **Erro técnico**\n\nStatus: ${
                err.response?.status || "N/A"
              }\nDetalhes: ${err.response?.data?.detail || err.message}`,
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
        content:
          "👋 Nova conversa iniciada.\n\nEstou com acesso total ao sistema. Como posso ajudar?",
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

          {isTyping && <div className="typing-indicator">🤖 Digitando...</div>}

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
