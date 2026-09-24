// Sidebar.jsx
// Left navigation panel: new chat button, chat history list, logout.

import { FiPlus, FiLogOut, FiMessageSquare } from "react-icons/fi";
import { useNavigate } from "react-router-dom";
import { getUserName, logout } from "../auth";

function Sidebar({ history, onNewChat, onSelectChat, activeChatId }) {
  const navigate = useNavigate();
  const userName = getUserName();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="w-72 h-screen bg-[#0F172A] text-white flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <h1 className="text-xl font-bold bg-gradient-to-r from-[#38BDF8] to-[#06B6D4] bg-clip-text text-transparent">
          MedAssist AI
        </h1>
      </div>

      {/* New Chat button */}
      <div className="p-4">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-gradient-to-r from-[#2563EB] to-[#06B6D4] hover:opacity-90 transition font-medium"
        >
          <FiPlus /> New Chat
        </button>
      </div>

      {/* Chat history list */}
      <div className="flex-1 overflow-y-auto px-3 space-y-1">
        <p className="text-xs text-slate-400 px-2 mb-2 uppercase tracking-wide">History</p>
        {history.length === 0 && (
          <p className="text-slate-500 text-sm px-2">No chats yet</p>
        )}
        {history.map((item) => (
          <button
            key={item.id}
            onClick={() => onSelectChat(item)}
            className={`w-full text-left px-3 py-2.5 rounded-lg flex items-start gap-2 text-sm transition ${
              activeChatId === item.id
                ? "bg-white/10 text-white"
                : "text-slate-300 hover:bg-white/5"
            }`}
          >
            <FiMessageSquare className="mt-0.5 flex-shrink-0" size={14} />
            {/* Truncate long questions so the sidebar stays tidy */}
            <span className="truncate">{item.question}</span>
          </button>
        ))}
      </div>

      {/* Footer: user info + logout */}
      <div className="p-4 border-t border-white/10 flex items-center justify-between">
        <span className="text-sm text-slate-300 truncate">{userName}</span>
        <button
          onClick={handleLogout}
          className="text-slate-400 hover:text-red-400 transition"
          title="Logout"
        >
          <FiLogOut size={18} />
        </button>
      </div>
    </div>
  );
}

export default Sidebar;