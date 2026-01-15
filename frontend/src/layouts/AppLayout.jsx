//E:\MAWDSLEYS-AGENTE\frontend\src\layouts\AppLayout.jsx

import Sidebar from "../components/Sidebar";
import { Outlet } from "react-router-dom";
import AIChatWidget from "../components/AIChatWidget";

export default function AppLayout() {
  return (
    <div className="layout">
      <Sidebar />
      <AIChatWidget />

      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
