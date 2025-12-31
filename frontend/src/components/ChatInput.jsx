// frontend/src/components/ChatInput.jsx
import React from "react";
import AudioInput from "./AudioInput";

export default function ChatInput({
  value,
  onChange,
  onSend,
  onKeyPress,
  isTyping,
  aiStatus,
}) {
  // Recebe texto vindo do áudio
  const handleAudioResult = (text) => {
    onChange(text);
  };

  return (
    <div className="input-section">
      <div className="input-wrapper">
        <textarea
          className="chat-input"
          placeholder="Digite ou fale com o Agente MAWDSLEYS..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={onKeyPress}
          rows="3"
          disabled={isTyping}
          style={{
            color: "#ffffff",
            backgroundColor: "rgba(255, 255, 255, 0.1)",
          }}
        />

        <div className="input-footer">
          <div className="input-hints">
            {aiStatus === "online"
              ? "✅ Conectado à OpenAI"
              : "⚠️ Verificando conexão"}
          </div>

          <div className="send-controls">
            {/* 🎤 ÁUDIO */}
            <AudioInput
              onResult={handleAudioResult}
              disabled={isTyping}
            />

            {/* ✈️ ENVIAR */}
            <button
              className="send-button"
              onClick={onSend}
              disabled={!value.trim() || isTyping}
            >
              {isTyping ? "⏳ Processando..." : "✈️ Enviar"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
