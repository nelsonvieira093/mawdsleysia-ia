//E: \MAWDSLEYS - AGENTE\frontend\src\App.jsx
import { AuthProvider } from "./contexts/AuthContext";
import RouterApp from "./Router";
import "./App.css";

export default function App() {
  return (
    <AuthProvider>
      <RouterApp />
    </AuthProvider>
  );
}
