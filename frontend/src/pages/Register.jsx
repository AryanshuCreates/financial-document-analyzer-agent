import { useState } from "react";
import api from "../api";
import { useNavigate, Link } from "react-router-dom";

export default function Register() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("viewer"); // default role
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert("Please fill in all fields");
      return;
    }

    setLoading(true);
    try {
      const res = await api.post("/register", { email, password, role });

      // Save JWT token
      localStorage.setItem("token", res.data.access_token);
      navigate("/dashboard"); // Redirect after successful registration
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="max-w-sm mx-auto mt-12 space-y-4 p-6 bg-white rounded-lg shadow-md"
    >
      <h2 className="text-2xl font-bold text-center text-purple-600">
        Register
      </h2>

      <input
        type="email"
        className="w-full border border-gray-300 rounded-lg p-2"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />

      <input
        type="password"
        className="w-full border border-gray-300 rounded-lg p-2"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      {/* Role dropdown */}
      <select
        value={role}
        onChange={(e) => setRole(e.target.value)}
        className="w-full border border-gray-300 rounded-lg p-2 bg-white text-gray-700"
      >
        <option value="viewer">Viewer</option>
        <option value="admin">Admin</option>
      </select>

      <button
        type="submit"
        className="bg-purple-600 text-white w-full py-2 rounded-lg hover:bg-purple-700 shadow"
        disabled={loading}
      >
        {loading ? "Registering..." : "Register"}
      </button>

      {/* Login link */}
      <p className="text-center text-gray-600 mt-2">
        Already have an account?{" "}
        <Link to="/login" className="text-purple-600 hover:underline">
          Login
        </Link>
      </p>
    </form>
  );
}
