import { useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";

export default function ProtectedRoute({ children }) {
  const { user } = useContext(AuthContext);

  if (!user && !localStorage.getItem("token")) {
    window.location.href = "/login";
    return null;
  }

  return children;
}
