import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

export default function useAuth() {
  const navigate = useNavigate();
  const [token, setToken] = useState(localStorage.getItem("access_token"));

  const login = (newToken) => {
    localStorage.setItem("access_token", newToken);
    setToken(newToken);
    navigate("/dashboard", { replace: true });
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setToken(null);
    navigate("/login", { replace: true });
  };

  const isAuthenticated = () => !!token;

  // Keep state in sync if localStorage changes elsewhere
  useEffect(() => {
    const handleStorage = () => setToken(localStorage.getItem("access_token"));
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);

  return { login, logout, isAuthenticated };
}
