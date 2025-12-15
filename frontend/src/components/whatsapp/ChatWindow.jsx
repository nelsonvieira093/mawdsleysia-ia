import React, { useEffect, useState } from "react";
import { getMessages, sendMessage } from "../../services/whatsapp";
import MessageBubble from "./MessageBubble";
import "./ChatWindow.css";

export default function ChatWindow({ conversationId }) {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");

  useEffect(() => {
    if (!conversationId) return;
    loadMessages();
  }, [conversationId]);

  async function loadMessages() {
    const msg = await getMessages(conversationId);
    setMessages(msg);
  }

  async function handleSend() {
    if (!text.trim()) return;

    await sendMessage(conversationId, text);
    setText("");
    loadMessages(); // atualizar chat
  }

  if (!conversationId)
    return (
      <div className="wa-chat-empty">
        Selecione uma conversa para começar
      </div>
    );

  return (
    <div className="wa-chat-window">
      <div className="wa-messages">
        {messages.map((m) => (
          <MessageBubble key={m.id} msg={m} />
        ))}
      </div>

      <div className="wa-input-area">
        <input
          type="text"
          placeholder="Digite uma mensagem…"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <button className="wa-send-btn" onClick={handleSend}>
          Enviar
        </button>
      </div>
    </div>
  );
}
