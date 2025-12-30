// frontend/src/components/WhatsAppButton.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import WhatsAppIcon from "./icons/WhatsAppIcon";
import "./WhatsAppButton.css";

export default function WhatsAppButton({
  to = "/whatsapp",
  label = "WhatsApp",
  small = false,
}) {
  const nav = useNavigate();
  const handleClick = (e) => {
    e.preventDefault();
    nav(to);
  };

  return (
    <button
      className={`wa-button ${small ? "wa-small" : ""}`}
      onClick={handleClick}
    >
      <WhatsAppIcon size={18} />
      <span className="wa-label">{label}</span>
    </button>
  );
}
