import { useNavigate } from "react-router-dom";

export default function useAuth() {
  const navigate = useNavigate();

  const login = (token) => {
    localStorage.setItem("access_token", token);
    navigate("/dashboard");
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  const isAuthenticated = () => {
    return !!localStorage.getItem("access_token");
  };

  return { login, logout, isAuthenticated };
}
