import { Link } from "react-router-dom";
import useAuth from "../hooks/useAuth";

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className="bg-white shadow-md px-6 py-3 flex justify-between items-center">
      <h1 className="font-bold text-xl text-purple-700">Financial Analyzer</h1>

      <div className="flex items-center space-x-4">
        {isAuthenticated ? (
          <>
            <Link
              to="/upload"
              className="text-gray-700 hover:text-purple-600 transition-colors"
            >
              Upload
            </Link>
            <Link
              to="/dashboard"
              className="text-gray-700 hover:text-purple-600 transition-colors"
            >
              Dashboard
            </Link>
            <button
              onClick={logout}
              className="px-3 py-1 rounded-lg bg-gray-200 hover:bg-purple-100 text-gray-700 transition-colors shadow-sm"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link
              to="/login"
              className="text-gray-700 hover:text-purple-600 transition-colors"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="px-3 py-1 rounded-lg bg-purple-600 text-white hover:bg-purple-700 transition-colors shadow-sm"
            >
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
