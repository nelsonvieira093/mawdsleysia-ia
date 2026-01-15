import React from "react";
import "./MessageBubble.css";

export default function MessageBubble({ msg }) {
  return (
    <div
      className={`wa-bubble ${msg.type === "received" ? "received" : "sent"}`}
    >
      {msg.text}
      <div className="wa-bubble-time">{msg.time}</div>
    </div>
  );
}
