// Dashboard.jsx
// The main chat interface — now wired to the real backend.

import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import ChatMessage from "../components/ChatMessage";
import { FiSend } from "react-icons/fi";
import api from "../api";

function Dashboard() {
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [activeChatId, setActiveChatId] = useState(null);
  const [loading, setLoading] = useState(false); // true while waiting for the AI's answer
  const [error, setError] = useState("");

  // Load chat history once when the dashboard first mounts
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await api.get("/history");
      setHistory(response.data.history);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setActiveChatId(null);
    setError("");
  };

  const handleSelectChat = (item) => {
    setMessages([
      { role: "user", content: item.question },
      { role: "assistant", content: item.answer, sources: item.sources },
    ]);
    setActiveChatId(item.id);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    const question = inputValue.trim();
    if (!question || loading) return;

    setError("");
    setInputValue("");

    // Immediately show the user's message
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const response = await api.post("/ask", { question });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.data.answer,
          sources: response.data.sources,
        },
      ]);

      // Refresh the sidebar so the new question appears in history
      fetchHistory();
    } catch (err) {
      if (err.response?.status === 401) {
        setError("Your session expired. Please log in again.");
      } else {
        setError("Something went wrong while getting your answer. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#F8FAFC]">
      <Sidebar
        history={history}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        activeChatId={activeChatId}
      />

      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <h2 className="text-2xl font-bold text-slate-700 mb-2">
                Ask MedAssist AI anything 🩺
              </h2>
              <p className="text-slate-500 max-w-md">
                Answers are generated only from your uploaded medical documents.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatMessage key={i} role={msg.role} content={msg.content} sources={msg.sources} />
          ))}

          {/* Typing indicator while waiting for the AI */}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#06B6D4] to-[#38BDF8] flex items-center justify-center flex-shrink-0">
                <span className="text-white text-xs">AI</span>
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3 shadow-sm">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
                </div>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="mx-6 mb-2 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-2">
            {error}
          </div>
        )}

        <form onSubmit={handleSend} className="p-4 border-t border-slate-200 bg-white">
          <div className="max-w-3xl mx-auto flex gap-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask a medical question..."
              disabled={loading}
              className="flex-1 px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:border-[#2563EB] transition disabled:bg-slate-50"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-3 rounded-xl bg-gradient-to-r from-[#2563EB] to-[#06B6D4] text-white hover:opacity-90 transition disabled:opacity-50"
            >
              <FiSend />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Dashboard;