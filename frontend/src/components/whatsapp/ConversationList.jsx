import React from "react";
import "./ConversationList.css";

export default function ConversationList({ conversations, active, onSelect }) {
  return (
    <div className="wa-conversation-list">
      <h3 className="wa-section-title">Conversas</h3>

      {conversations.map((c) => (
        <div
          key={c.id}
          className={`wa-conversation-item ${active === c.id ? "active" : ""}`}
          onClick={() => onSelect(c.id)}
        >
          <div className="wa-conversation-name">{c.name}</div>
          <div className="wa-conversation-last">{c.lastMessage}</div>
        </div>
      ))}

      {conversations.length === 0 && (
        <p className="wa-empty">Nenhuma conversa ainda.</p>
      )}
    </div>
  );
}
