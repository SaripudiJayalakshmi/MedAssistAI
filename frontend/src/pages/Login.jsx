// Login.jsx
// Glassmorphism login page — collects email/password, calls /login, stores the token.

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FiMail, FiLock } from "react-icons/fi";
import api from "../api";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); // lets us redirect after a successful login

  const handleSubmit = async (e) => {
    e.preventDefault(); // stop the browser's default full-page form submission
    setError("");
    setLoading(true);

    try {
      const response = await api.post("/login", { email, password });

      if (response.data.error) {
        setError(response.data.error);
      } else {
        // Save the token so future requests can prove we're logged in
        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("userName", response.data.name);
        navigate("/dashboard"); // we'll build this page in 9c
      }
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0F172A] via-[#1E3A8A] to-[#0F172A] px-4">
      <div className="w-full max-w-md">
        {/* Glassmorphism card: semi-transparent background + backdrop blur */}
        <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl shadow-2xl p-8">
          <h1 className="text-3xl font-bold text-white text-center mb-1">MedAssist AI</h1>
          <p className="text-slate-300 text-center mb-8">Sign in to continue</p>

          {error && (
            <div className="bg-red-500/20 border border-red-500/40 text-red-200 text-sm rounded-lg px-4 py-2 mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-slate-400 focus:outline-none focus:border-[#38BDF8] transition"
              />
            </div>

            <div className="relative">
              <FiLock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-slate-400 focus:outline-none focus:border-[#38BDF8] transition"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-lg bg-gradient-to-r from-[#2563EB] to-[#06B6D4] text-white font-semibold hover:opacity-90 transition disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Login"}
            </button>
          </form>

          <p className="text-slate-400 text-center text-sm mt-6">
            Don't have an account?{" "}
            <Link to="/register" className="text-[#38BDF8] hover:underline">
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;