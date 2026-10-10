import ReactMarkdown from "react-markdown";
import { FiUser, FiCpu, FiCopy, FiThumbsUp, FiThumbsDown, FiTrash2, FiDownload, FiBookmark } from "react-icons/fi";
import { useState } from "react";
import api from "../api";
import remarkGfm from "remark-gfm";

function ChatMessage({ id, role, content, sources, onDeleted, bookmarked: initialBookmarked }) {
  const isUser = role === "user";
  const [feedback, setFeedback] = useState(null);
  const [copied, setCopied] = useState(false);

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

        {!isUser && (
          <div className="mt-3 pt-2 border-t border-slate-100 flex items-center gap-3 text-slate-400">
            <button onClick={handleCopy} title="Copy" className="hover:text-slate-700 transition">
              <FiCopy size={14} />
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
              <button onClick={handleDelete} title="Delete" className="hover:text-red-600 transition ml-auto">
                <FiTrash2 size={14} />
              </button>
            )}
            {copied && <span className="text-xs text-green-600">Copied!</span>}
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;