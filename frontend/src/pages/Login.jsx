import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";

export default function Login({ onLogin }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert("Please fill in all fields");
      return;
    }

    setLoading(true);
    try {
      const res = await api.post("/login", { email, password });
      localStorage.setItem("token", res.data.access_token);

      onLogin();
      navigate("/dashboard", { replace: true });
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="max-w-sm mx-auto mt-16 p-6 bg-white rounded-xl shadow-md space-y-4"
    >
      <h2 className="text-2xl font-bold text-center text-purple-700">Login</h2>

      <input
        type="email"
        className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-purple-300"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />

      <input
        type="password"
        className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-purple-300"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      <button
        type="submit"
        className="bg-purple-600 text-white w-full py-2 rounded-lg hover:bg-purple-700 shadow"
        disabled={loading}
      >
        {loading ? "Logging in..." : "Login"}
      </button>

      <p className="text-center text-gray-600 text-sm">
        Don’t have an account?{" "}
        <Link to="/register" className="text-purple-600 hover:underline">
          Register
        </Link>
      </p>
    </form>
  );
}
