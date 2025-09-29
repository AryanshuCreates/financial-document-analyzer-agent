import { useState } from "react";
import api from "../api";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [docId, setDocId] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Choose a PDF file");

    const fd = new FormData();
    fd.append("file", file);
    fd.append("query", "Summarize financial insights");

    try {
      const res = await api.post("/analyze", fd, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (e) => {
          setProgress(Math.round((e.loaded * 100) / e.total));
        },
      });
      setDocId(res.data.document_id);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Upload failed");
    }
  };

  return (
    <div className="max-w-md mx-auto mt-12 space-y-4">
      <h2 className="text-xl font-bold">Upload Financial Document</h2>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button
        onClick={handleUpload}
        className="bg-blue-600 text-white px-4 py-2 w-full"
      >
        Upload
      </button>
      {progress > 0 && <div>Progress: {progress}%</div>}
      {docId && <div className="text-green-600">Queued with ID: {docId}</div>}
    </div>
  );
}
