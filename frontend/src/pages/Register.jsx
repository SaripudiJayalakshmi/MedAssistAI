// Register.jsx
// Same glassmorphism style as Login, but collects name/email/password/confirm.

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FiUser, FiMail, FiLock } from "react-icons/fi";
import api from "../api";

function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const response = await api.post("/register", { name, email, password });

      if (response.data.error) {
        setError(response.data.error);
      } else {
        setSuccess(true);
        // Give the user a moment to see the success message, then send them to login
        setTimeout(() => navigate("/login"), 1500);
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
        <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl shadow-2xl p-8">
          <h1 className="text-3xl font-bold text-white text-center mb-1">Create Account</h1>
          <p className="text-slate-300 text-center mb-8">Join MedAssist AI</p>

          {error && (
            <div className="bg-red-500/20 border border-red-500/40 text-red-200 text-sm rounded-lg px-4 py-2 mb-4">
              {error}
            </div>
          )}
          {success && (
            <div className="bg-green-500/20 border border-green-500/40 text-green-200 text-sm rounded-lg px-4 py-2 mb-4">
              Account created! Redirecting to login...
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <FiUser className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-slate-400 focus:outline-none focus:border-[#38BDF8] transition"
              />
            </div>

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

            <div className="relative">
              <FiLock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="password"
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-slate-400 focus:outline-none focus:border-[#38BDF8] transition"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-lg bg-gradient-to-r from-[#2563EB] to-[#06B6D4] text-white font-semibold hover:opacity-90 transition disabled:opacity-50"
            >
              {loading ? "Creating account..." : "Register"}
            </button>
          </form>

          <p className="text-slate-400 text-center text-sm mt-6">
            Already have an account?{" "}
            <Link to="/login" className="text-[#38BDF8] hover:underline">
              Login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Register;