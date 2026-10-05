import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FiTrash2, FiFileText, FiUsers, FiMessageSquare, FiDatabase, FiUpload } from "react-icons/fi";
import api from "../api";

function Admin() {
  const [documents, setDocuments] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [docsRes, analyticsRes] = await Promise.all([
        api.get("/admin/documents"),
        api.get("/admin/analytics"),
      ]);
      setDocuments(docsRes.data.documents);
      setAnalytics(analyticsRes.data);
    } catch (err) {
      if (err.response?.status === 403) {
        setError("Admin access required.");
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setFile(null);
      loadData();
    } catch (err) {
      setError("Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename) => {
    if (!confirm(`Delete "${filename}"?`)) return;
    try {
      await api.delete(`/admin/documents/${encodeURIComponent(filename)}`);
      loadData();
    } catch (err) {
      setError("Delete failed.");
    }
  };

  if (error === "Admin access required.") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC]">
        <div className="text-center">
          <p className="text-red-500 font-semibold mb-4">Admin access required.</p>
          <button onClick={() => navigate("/dashboard")} className="text-[#2563EB] underline">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] p-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-slate-800">Admin Dashboard</h1>
          <button onClick={() => navigate("/dashboard")} className="text-sm text-[#2563EB] hover:underline">
            Back to Chat
          </button>
        </div>

        {/* Analytics cards */}
        {analytics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { icon: FiUsers, label: "Users", value: analytics.total_users },
              { icon: FiMessageSquare, label: "Questions Asked", value: analytics.total_questions_asked },
              { icon: FiFileText, label: "Documents", value: analytics.total_documents },
              { icon: FiDatabase, label: "Chunks in DB", value: analytics.total_chunks_in_db },
            ].map((stat) => (
              <div key={stat.label} className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
                <stat.icon className="text-[#2563EB] mb-2" size={20} />
                <p className="text-2xl font-bold text-slate-800">{stat.value}</p>
                <p className="text-sm text-slate-500">{stat.label}</p>
              </div>
            ))}
          </div>
        )}

        {/* Upload form */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm mb-6">
          <h2 className="font-semibold text-slate-800 mb-4">Upload Document</h2>
          {error && error !== "Admin access required." && (
            <p className="text-red-500 text-sm mb-3">{error}</p>
          )}
          <form onSubmit={handleUpload} className="flex items-center gap-3">
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files[0])}
              className="flex-1 text-sm"
            />
            <button
              type="submit"
              disabled={uploading || !file}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-[#2563EB] to-[#06B6D4] text-white text-sm font-medium disabled:opacity-50"
            >
              <FiUpload /> {uploading ? "Uploading..." : "Upload"}
            </button>
          </form>
        </div>

        {/* Document list */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <h2 className="font-semibold text-slate-800 p-6 pb-0 mb-4">Uploaded Documents</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="px-6 py-2">Filename</th>
                <th className="px-6 py-2">Chunks</th>
                <th className="px-6 py-2"></th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.filename} className="border-b border-slate-100">
                  <td className="px-6 py-3 flex items-center gap-2">
                    <FiFileText className="text-slate-400" size={14} /> {doc.filename}
                  </td>
                  <td className="px-6 py-3 text-slate-500">{doc.chunk_count}</td>
                  <td className="px-6 py-3 text-right">
                    <button onClick={() => handleDelete(doc.filename)} className="text-red-400 hover:text-red-600">
                      <FiTrash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
              {documents.length === 0 && (
                <tr>
                  <td colSpan={3} className="px-6 py-6 text-center text-slate-400">No documents yet</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Admin;