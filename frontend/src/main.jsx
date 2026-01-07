//E: \MAWDSLEYS - AGENTE\frontend\src\main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import RouterApp from "./Router";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <AuthProvider>
    <BrowserRouter>
      <RouterApp />
    </BrowserRouter>
  </AuthProvider>
);
