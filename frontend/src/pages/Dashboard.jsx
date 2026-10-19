// Dashboard.jsx
// The main chat interface — now wired to the real backend.

import { useState, useEffect, useRef } from "react";
import Sidebar from "../components/Sidebar";
import ChatMessage from "../components/ChatMessage";
import { FiSend, FiPaperclip, FiImage, FiMic, FiMicOff } from "react-icons/fi";
import api from "../api";
import { isAdmin } from "../auth";

function Dashboard() {
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [activeChatId, setActiveChatId] = useState(null);
  const [loading, setLoading] = useState(false); // true while waiting for the AI's answer
  const [error, setError] = useState("");
  const fileRef = useRef(null);
  const [uploadMsg, setUploadMsg] = useState("");

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    setUploadMsg("Uploading...");
    try {
      await api.post("/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
      setUploadMsg("Uploaded: " + file.name);
    } catch (err) {
      setUploadMsg(err.response?.data?.detail || "Upload failed");
    }
    e.target.value = "";
  };
  const imgRef = useRef(null);

  const handleImage = async (e) => {
    const file = e.target.files[0];
    e.target.value = "";
    if (!file) return;
    const q = inputValue.trim();
    setMessages((prev) => [...prev, { role: "user", content: "🖼️ " + file.name + (q ? " — " + q : "") }]);
    setInputValue("");
    setLoading(true);
    setError("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("question", q);
      const res = await api.post("/ask-image", fd, { headers: { "Content-Type": "multipart/form-data" } });
      setMessages((prev) => [...prev, { role: "assistant", content: res.data.answer, sources: [], id: res.data.message_id }]);
    } catch (err) {
      setError(err.response?.data?.detail || "Image analysis failed");
    } finally {
      setLoading(false);
    }
  };
  const recRef = useRef(null);
const [listening, setListening] = useState(false);

const toggleMic = () => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { setError("Voice input is not supported in this browser. Use Chrome or Edge."); return; }
  if (listening) { recRef.current?.stop(); return; }
  const rec = new SR();
  rec.lang = "en-US";
  rec.interimResults = true;
  rec.continuous = false;
  const base = inputValue ? inputValue + " " : "";
  rec.onresult = (ev) => {
    let t = "";
    for (let i = 0; i < ev.results.length; i++) t += ev.results[i][0].transcript;
    setInputValue(base + t);
  };
  rec.onerror = (ev) => { setError(ev.error === "not-allowed" ? "Microphone permission denied." : "Voice error: " + ev.error); setListening(false); };
  rec.onend = () => setListening(false);
  recRef.current = rec;
  rec.start();
  setListening(true);
};

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
        {
            role: "assistant",
            content: item.answer,
            sources: item.sources,
            id: item.id,
            bookmarked: item.bookmarked
        },
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
            evidence: response.data.evidence,
            grounded: response.data.grounded,
            id: response.data.message_id,
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
  const handleShowBookmarks = async () => {
    try {
      const res = await api.get("/bookmarks");
      const bookmarkMsgs = res.data.bookmarks.flatMap((b) => [
        { role: "user", content: b.question },
        { role: "assistant", content: b.answer, sources: b.sources, id: b.id, bookmarked: true },
      ]);
      setMessages(bookmarkMsgs);
      setActiveChatId("bookmarks");
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex h-screen bg-[#F8FAFC]">
      <Sidebar
        history={history}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        activeChatId={activeChatId}
        onShowBookmarks={handleShowBookmarks}
      />

      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <h2 className="text-2xl font-bold text-slate-700 mb-2">
                Ask MedAssist AI anything 🩺
              </h2>
              <p className="text-slate-500 max-w-md">
                Answers use your uploaded documents and general medical knowledge, with sources labeled.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatMessage
                key={i}
                id={msg.id}
                role={msg.role}
                content={msg.content}
                sources={msg.sources}
                evidence={msg.evidence}
                grounded={msg.grounded}
                onDeleted={(deletedId) => {
                setMessages((prev) => prev.filter((m) => m.id !== deletedId));
                fetchHistory();
                }}
            />
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
        {uploadMsg && (
          <p className="text-xs text-gray-500 px-2 pb-1">
            {uploadMsg}
          </p>
        )}

        <form onSubmit={handleSend} className="p-4 border-t border-slate-200 bg-white">
          <div className="max-w-3xl mx-auto flex gap-3">
            {isAdmin() && (
              <>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".pdf"
                  className="hidden"
                  onChange={handleUpload}
                />
                

                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  title="Upload PDF"
                  className="p-2 text-gray-500 hover:text-blue-600"
                >
                  <FiPaperclip />
                </button>
              </>
            )}
            <input
              ref={imgRef}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              className="hidden"
              onChange={handleImage}
            />

            <button
              type="button"
              onClick={() => imgRef.current?.click()}
              title="Ask about an image"
              className="p-2 text-gray-500 hover:text-blue-600"
            >
              <FiImage />
            </button>
            <button
              type="button"
              onClick={toggleMic}
              title={listening ? "Stop listening" : "Voice input"}
              className={
                "p-2 " +
                (listening
                  ? "text-red-500 animate-pulse"
                  : "text-gray-500 hover:text-blue-600")
              }
            >
              {listening ? <FiMicOff /> : <FiMic />}
            </button>
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