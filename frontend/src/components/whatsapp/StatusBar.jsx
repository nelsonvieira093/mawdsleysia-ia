import React from "react";
import "./StatusBar.css";

export default function StatusBar({ data }) {
  const status = data?.status === "active" ? "online" : "offline";
  const lastUpdate = data?.timestamp || "--";

  return (
    <div className="status-bar">
      {/* Lado esquerdo */}
      <div className="status-left">
        <span
          className={`status-indicator ${
            status === "online" ? "status-online" : "status-offline"
          }`}
        ></span>

        <span className="status-title">
          Webhook do WhatsApp — {status === "online" ? "Online" : "Offline"}
        </span>
      </div>

      {/* Lado direito */}
      <div className="status-right">
        <span className="status-last-update">Atualizado: {lastUpdate}</span>

        <button
          className="status-btn"
          onClick={() => window.location.reload()}
        >
          Atualizar
        </button>
      </div>
    </div>
  );
}
