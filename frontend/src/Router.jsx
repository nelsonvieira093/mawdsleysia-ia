// frontend/src/Router.jsx

import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";

import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import Agent from "./pages/Agent";
import Deliverables from "./pages/Deliverables";
import WeeklyAgenda from "./pages/WeeklyAgenda";
import History from "./pages/History";
import KnowledgeBase from "./pages/KnowledgeBase";
import MeetingDetails from "./pages/MeetingDetails";
import WhatsApp from "./pages/WhatsApp";

import Login from "./pages/Login";
import Signup from "./pages/Signup";

export default function RouterApp() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="spinner-fullscreen" />;
  }

  return (
    <Routes>
      {/* ================= ROTAS PÚBLICAS ================= */}
      <Route
        path="/login"
        element={user ? <Navigate to="/dashboard" replace /> : <Login />}
      />

      <Route
        path="/signup"
        element={user ? <Navigate to="/dashboard" replace /> : <Signup />}
      />

      {/* ================= ROTAS PROTEGIDAS ================= */}
      <Route
        path="/*"
        element={
          user ? (
            <div className="app-container">
              <Sidebar />
              <main className="main-content">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/chat" element={<Chat />} />
                  <Route path="/agent" element={<Agent />} />
                  <Route path="/deliverables" element={<Deliverables />} />
                  <Route path="/agenda" element={<WeeklyAgenda />} />
                  <Route path="/agenda/:id" element={<MeetingDetails />} />
                  <Route path="/history" element={<History />} />
                  <Route path="/kb" element={<KnowledgeBase />} />
                  <Route path="/whatsapp" element={<WhatsApp />} />
                  <Route
                    path="*"
                    element={<Navigate to="/dashboard" replace />}
                  />
                </Routes>
              </main>
            </div>
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
    </Routes>
  );
}
