// Dashboard.jsx
// The main chat interface — sidebar + message area + input box.
// (Stage 9c: layout + local state only. Stage 9d wires up real API calls.)

import { useState } from "react";
import Sidebar from "../components/Sidebar";
import ChatMessage from "../components/ChatMessage";
import { FiSend } from "react-icons/fi";

function Dashboard() {
  const [messages, setMessages] = useState([]); // current conversation on screen
  const [history, setHistory] = useState([]);   // past questions, shown in sidebar
  const [inputValue, setInputValue] = useState("");
  const [activeChatId, setActiveChatId] = useState(null);

  const handleNewChat = () => {
    setMessages([]);
    setActiveChatId(null);
  };

  const handleSelectChat = (item) => {
    // For now, just show that single past Q&A — Stage 9e will load full history properly
    setMessages([
      { role: "user", content: item.question },
      { role: "assistant", content: item.answer, sources: item.sources },
    ]);
    setActiveChatId(item.id);
  };

  const handleSend = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    // TEMPORARY: just echo locally so we can see the UI working.
    // Stage 9d replaces this with a real call to POST /ask.
    setMessages((prev) => [
      ...prev,
      { role: "user", content: inputValue },
      {
        role: "assistant",
        content: "*(This is a placeholder response — real AI answers come in Stage 9d)*",
        sources: [],
      },
    ]);
    setInputValue("");
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
        {/* Message area */}
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
        </div>

        {/* Input box */}
        <form onSubmit={handleSend} className="p-4 border-t border-slate-200 bg-white">
          <div className="max-w-3xl mx-auto flex gap-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask a medical question..."
              className="flex-1 px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:border-[#2563EB] transition"
            />
            <button
              type="submit"
              className="px-5 py-3 rounded-xl bg-gradient-to-r from-[#2563EB] to-[#06B6D4] text-white hover:opacity-90 transition"
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