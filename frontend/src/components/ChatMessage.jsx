// ChatMessage.jsx
// Renders a single message bubble — either the user's question or the AI's answer.

import ReactMarkdown from "react-markdown";
import { FiUser, FiCpu } from "react-icons/fi";

function ChatMessage({ role, content, sources }) {
  const isUser = role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? "bg-[#2563EB]" : "bg-gradient-to-br from-[#06B6D4] to-[#38BDF8]"
        }`}
      >
        {isUser ? <FiUser className="text-white" size={16} /> : <FiCpu className="text-white" size={16} />}
      </div>

      {/* Message bubble */}
      <div
        className={`max-w-2xl rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-[#2563EB] text-white"
            : "bg-white border border-slate-200 text-slate-800 shadow-sm"
        }`}
      >
        {isUser ? (
          <p>{content}</p>
        ) : (
          // react-markdown converts **bold**, bullet lists, etc. into real HTML
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        )}

        {/* Show source citations, if any */}
        {sources && sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-200 flex flex-wrap gap-2">
            {sources.map((src, i) => (
              <span
                key={i}
                className="text-xs bg-[#38BDF8]/10 text-[#0369A1] px-2 py-1 rounded-full"
              >
                📄 {src}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;