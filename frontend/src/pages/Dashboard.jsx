import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";

export default function Dashboard() {
  const [docs, setDocs] = useState([]);

  const fetchDocs = async () => {
    try {
      const res = await api.get("/documents");
      setDocs(res.data);
    } catch {
      console.error("Failed to fetch documents");
    }
  };

  useEffect(() => {
    fetchDocs();
    const interval = setInterval(fetchDocs, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-2xl mx-auto mt-12">
      <h2 className="text-xl font-bold mb-4">Your Documents</h2>
      <ul className="space-y-2">
        {docs.map((d) => (
          <li key={d._id} className="border p-3 rounded bg-white shadow">
            <p>
              <strong>{d.filename}</strong>
            </p>
            <p>Status: {d.status}</p>
            <Link
              to={`/analysis/${d._id}`}
              className="text-blue-600 underline mt-2 inline-block"
            >
              View Results
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
