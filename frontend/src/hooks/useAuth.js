import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

export default function useAuth() {
  const navigate = useNavigate();
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [isAuthenticatedState, setIsAuthenticatedState] = useState(!!token);

  const login = (newToken) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setIsAuthenticatedState(true);
    navigate("/dashboard", { replace: true });
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setIsAuthenticatedState(false);
    navigate("/login", { replace: true });
    window.location.reload();
    console.log("Logged out successfully");
  };

  useEffect(() => {
    setIsAuthenticatedState(!!token);
  }, [token]);

  useEffect(() => {
    const handleStorage = () => {
      const newToken = localStorage.getItem("token");
      setToken(newToken);
      setIsAuthenticatedState(!!newToken);
    };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, [token]);

  return { login, logout, isAuthenticatedState };
}
