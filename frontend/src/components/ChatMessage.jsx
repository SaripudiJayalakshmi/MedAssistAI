import ReactMarkdown from "react-markdown";
import { FiUser, FiCpu, FiCopy, FiThumbsUp, FiThumbsDown, FiTrash2, FiDownload, FiBookmark, FiFileText, FiVolume2, FiVolumeX } from "react-icons/fi";
import { useState, useEffect } from "react";
import api from "../api";
import remarkGfm from "remark-gfm";

function ChatMessage({ id, role, content, sources, evidence, grounded, onDeleted, bookmarked: initialBookmarked }) {
  const isUser = role === "user";
  const [feedback, setFeedback] = useState(null);
  const [copied, setCopied] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  useEffect(() => () => { if ("speechSynthesis" in window) window.speechSynthesis.cancel(); }, []);

  const handleSpeak = () => {
    if (!("speechSynthesis" in window)) return;
    if (speaking) { window.speechSynthesis.cancel(); setSpeaking(false); return; }
    window.speechSynthesis.cancel();
    const clean = content
      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
      .replace(/[#*_`>|~]/g, " ")
      .replace(/^\s*-\s+/gm, "")
      .replace(/\s+/g, " ")
      .trim();
    const chunks = clean.match(/[^.!?]+[.!?]*\s*/g) || [clean];
    chunks.forEach((c, i) => {
      const u = new SpeechSynthesisUtterance(c);
      u.lang = "en-US";
      if (i === chunks.length - 1) u.onend = () => setSpeaking(false);
      u.onerror = (e) => { if (e.error !== "canceled" && e.error !== "interrupted") setSpeaking(false); };
      window.speechSynthesis.speak(u);
    });
    setSpeaking(true);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleFeedback = async (type) => {
    if (!id) return;
    setFeedback(type);
    try {
      await api.patch(`/history/${id}/feedback`, { feedback: type });
    } catch (err) {
      console.error("Feedback failed:", err);
    }
  };
  const [bookmarked, setBookmarked] = useState(initialBookmarked || false);

const handleBookmark = async () => {
  if (!id) return;

  try {
    const res = await api.patch(`/history/${id}/bookmark`);
    setBookmarked(res.data.bookmarked);
  } catch (err) {
    console.error("Bookmark failed:", err);
  }
};

  const handleDelete = async () => {
    if (!id) return;
    if (!confirm("Delete this message?")) return;
    try {
      await api.delete(`/history/${id}`);
      onDeleted?.(id);
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };
  const handleExport = async () => {
      if (!id) return;
      try {
          const response = await api.get(`/export/${id}/pdf`, { responseType: "blob" });
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", "medassist_answer.pdf");
          document.body.appendChild(link);
          link.click();
          link.remove();
      } catch (err) {
      console.error("Export failed:", err);
    }
  };
  const handleExportDocx = async () => {
    if (!id) return;
    try {
      const response = await api.get(`/export/${id}/docx`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "medassist_answer.docx");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("DOCX export failed:", err);
    }
  };


  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? "bg-[#2563EB]" : "bg-gradient-to-br from-[#06B6D4] to-[#38BDF8]"}`}>
        {isUser ? <FiUser className="text-white" size={16} /> : <FiCpu className="text-white" size={16} />}
      </div>

      <div className={`max-w-2xl rounded-2xl px-4 py-3 ${isUser ? "bg-[#2563EB] text-white" : "bg-white border border-slate-200 text-slate-800 shadow-sm"}`}>
        {isUser ? (
          <p>{content}</p>
        ) : (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          </div>
        )}

        {sources && sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-200 flex flex-wrap gap-2">
            {sources.map((src, i) => (
              <span key={i} className="text-xs bg-[#38BDF8]/10 text-[#0369A1] px-2 py-1 rounded-full">📄 {src}</span>
            ))}
          </div>
        )}
        {evidence && evidence.length > 0 && (
          <details className="mt-3 text-sm">
            <summary className="cursor-pointer text-blue-600 font-medium">View evidence ({evidence.length})</summary>
            <div className="mt-2 space-y-2">
              {evidence.map((e, i) => (
                <div key={i} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <div className="text-xs font-semibold text-slate-700">{e.document}{e.page ? ", page " + e.page : ""}</div>
                  <p className="mt-1 text-xs text-slate-600">{(e.passage || "").replace(/\u0000/g, "f")}…</p>
                </div>
              ))}
            </div>
          </details>
        )}
        {grounded === false && (
          <div className="mt-3 text-xs rounded-lg bg-amber-50 border border-amber-200 text-amber-800 px-3 py-2">No supporting passage was found in the uploaded documents. This answer is based on general medical knowledge.</div>
        )}

        {!isUser && (
          <div className="mt-3 pt-2 border-t border-slate-100 flex items-center gap-3 text-slate-400">
            <button onClick={handleCopy} title="Copy" className="hover:text-slate-700 transition">
              <FiCopy size={14} />
            </button>
            <button
              type="button"
              onClick={handleSpeak}
              title={speaking ? "Stop reading" : "Read aloud"}
              className="p-1 text-gray-500 hover:text-blue-600"
            >
              {speaking ? <FiVolumeX /> : <FiVolume2 />}
            </button>
            <button onClick={() => handleFeedback("like")} title="Like" className={`hover:text-green-600 transition ${feedback === "like" ? "text-green-600" : ""}`}>
              <FiThumbsUp size={14} />
            </button>
            <button onClick={() => handleFeedback("dislike")} title="Dislike" className={`hover:text-red-600 transition ${feedback === "dislike" ? "text-red-600" : ""}`}>
              <FiThumbsDown size={14} />
            </button>
            <button onClick={handleBookmark} title="Bookmark" className={`hover:text-yellow-500 transition ${bookmarked ? "text-yellow-500" : ""}`}>
              <FiBookmark size={14} fill={bookmarked ? "currentColor" : "none"} />
            </button>
            {id && (
              <>
                <button onClick={handleExport} title="Export PDF" className="hover:text-blue-600 transition">
                  <FiDownload size={14} />
                </button>
                <button onClick={handleExportDocx} title="Export DOCX" className="hover:text-blue-600 transition">
                  <FiFileText size={14} />
                </button>
                <button onClick={handleDelete} title="Delete" className="hover:text-red-600 transition ml-auto">
                  <FiTrash2 size={14} />
                </button>
              </>
            )}
            {copied && <span className="text-xs text-green-600">Copied!</span>}
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;