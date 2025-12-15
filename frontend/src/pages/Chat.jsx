// frontend/src/pages/Chat.jsx
import React, { useState, useEffect, useRef } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";
import "./Chat.css";

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      content: "👋 Olá! Eu sou o **Agente MAWDSLEYS**, seu assistente de inteligência corporativa. Posso ajudar com:\n\n• 📊 Análise de documentos\n• 🔄 Geração de follow-ups\n• 📅 Planejamento de pautas\n• 🔍 Consultas estratégicas\n\nComo posso ajudá-lo hoje?",
      timestamp: new Date().toISOString()
    }
  ]);
  
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [aiStatus, setAiStatus] = useState("checking");
  const messagesEndRef = useRef(null);

  // Verificar status da OpenAI
  useEffect(() => {
    checkAIStatus();
  }, []);

  // Scroll automático
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const checkAIStatus = async () => {
    try {
      const response = await api.get("/chat/health");
      setAiStatus(response.data.status);
    } catch (error) {
      setAiStatus("offline");
      console.error("Erro ao verificar status:", error);
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const suggestedTopics = [
    "Analisar relatório financeiro",
    "Gerar follow-ups automáticos",
    "Criar pauta semanal",
    "Consultar base de conhecimento",
    "Analisar tendências de mercado"
  ];

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isTyping) return;

    // Adicionar mensagem do usuário
    const userMessage = {
      id: Date.now(),
      role: "user",
      content: inputMessage,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage("");
    setIsTyping(true);

    try {
      // Chamar OpenAI via backend
      const response = await api.post("/chat/", {
        message: messageToSend,
        model: "gpt-3.5-turbo",
        temperature: 0.7,
        max_tokens: 1000
      });
      
      // Adicionar resposta da IA
      const aiMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: response.data.reply,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error("Erro ao enviar mensagem:", error);
      
      // Mensagem de fallback
      const fallbackMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: "🔧 **Ops!** Estou com dificuldades técnicas no momento.\n\nPor favor, tente novamente em alguns instantes.",
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickTopic = (topic) => {
    setInputMessage(topic);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        role: "assistant",
        content: "👋 Olá! Eu sou o **Agente MAWDSLEYS**, seu assistente de inteligência corporativa. Como posso ajudá-lo hoje?",
        timestamp: new Date().toISOString()
      }
    ]);
  };

  return (
    <div className="chat-page-container">
      <Sidebar />
      
      <div className="chat-main-area">
        <div className="chat-header">
          <div className="header-left">
            <div className="title-row">
              <h1>Chat MAWDSLEYS</h1>
              <div className={`ai-status ${aiStatus}`}>
                <span className="status-dot"></span>
                {aiStatus === "online" ? "IA Online" : "IA Offline"}
              </div>
            </div>
            <p className="subtitle">Converse com o agente de inteligência corporativa</p>
          </div>
          
          <div className="header-right">
            <button className="clear-btn" onClick={clearChat} disabled={isTyping}>
              🗑️ Nova Conversa
            </button>
          </div>
        </div>

        <div className="chat-content">
          {/* Sugestões rápidas */}
          <div className="suggestions-section">
            <h3>📋 Tópicos Sugeridos</h3>
            <div className="suggestions-grid">
              {suggestedTopics.map((topic, index) => (
                <button
                  key={index}
                  className="suggestion-btn"
                  onClick={() => handleQuickTopic(topic)}
                  disabled={isTyping}
                >
                  {topic}
                </button>
              ))}
            </div>
          </div>

          {/* Área de mensagens */}
          <div className="messages-container">
            <div className="messages-box">
              {messages.map((message) => (
                <div 
                  key={message.id} 
                  className={`message-wrapper ${message.role === "user" ? "user-message" : "bot-message"}`}
                >
                  <div className="message-avatar">
                    {message.role === "user" ? "👤" : "🤖"}
                  </div>
                  <div className="message-content">
                    <div className="message-header">
                      <div className="message-sender">
                        {message.role === "user" ? "Você" : "Agente MAWDSLEYS"}
                      </div>
                      <span className="message-time">{formatTime(message.timestamp)}</span>
                    </div>
                    <div className={`message-text ${message.role === "user" ? "user-text" : "bot-text"}`}>
                      {message.content.split('\n').map((line, i) => (
                        <React.Fragment key={i}>
                          {line}
                          {i < message.content.split('\n').length - 1 && <br />}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="typing-indicator">
                  <div className="typing-avatar">🤖</div>
                  <div className="typing-content">
                    <div className="typing-dots">
                      <span className="dot"></span>
                      <span className="dot"></span>
                      <span className="dot"></span>
                    </div>
                    <span className="typing-text">Digitando...</span>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Área de input - COM TEXTO BRANCO GARANTIDO */}
          <div className="input-section">
            <div className="input-wrapper">
              <textarea
                className="chat-input"
                placeholder="Digite sua mensagem para o Agente MAWDSLEYS..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                rows="3"
                disabled={isTyping}
                style={{ 
                  color: '#ffffff', // Texto branco forçado
                  backgroundColor: 'rgba(255, 255, 255, 0.1)'
                }}
              />
              
              <div className="input-footer">
                <div className="input-hints">
                  {aiStatus === "online" ? "✅ Conectado à OpenAI" : "⚠️ Verificando conexão"}
                </div>
                
                <div className="send-controls">
                  <button 
                    className="send-button"
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isTyping}
                  >
                    {isTyping ? (
                      <>
                        <span className="loading-icon">⏳</span>
                        Processando...
                      </>
                    ) : (
                      <>
                        <span className="send-icon">✈️</span>
                        Enviar
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}