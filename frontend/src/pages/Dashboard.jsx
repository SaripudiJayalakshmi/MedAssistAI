// Dashboard.jsx
// Placeholder for now — full ChatGPT-style layout comes in Stage 9c.

import { useNavigate } from "react-router-dom";
import { getUserName, logout } from "../auth";

function Dashboard() {
  const navigate = useNavigate();
  const userName = getUserName();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
      <div className="bg-white shadow-lg rounded-2xl p-8 text-center">
        <h1 className="text-2xl font-bold text-[#2563EB] mb-2">
          Welcome, {userName}! 👋
        </h1>
        <p className="text-slate-600 mb-6">
          This is a placeholder — the real chat dashboard comes next.
        </p>
        <button
          onClick={handleLogout}
          className="px-6 py-2 rounded-lg bg-red-500 text-white font-semibold hover:bg-red-600 transition"
        >
          Logout
        </button>
      </div>
    </div>
  );
}

export default Dashboard;