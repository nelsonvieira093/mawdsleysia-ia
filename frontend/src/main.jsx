//E: \MAWDSLEYS - AGENTE\frontend\src\main.jsx
// src/main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { AIProvider } from "./contexts/AIContext"; // ⬅️ ADICIONE ESTE IMPORT
import RouterApp from "./Router";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <AuthProvider>
    <BrowserRouter>
      <AIProvider> {/* ⬅️ ENVOLVA O RouterApp COM AIProvider */}
        <RouterApp />
      </AIProvider>
    </BrowserRouter>
  </AuthProvider>
);
