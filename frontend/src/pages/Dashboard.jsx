import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";

export default function Dashboard() {
  const [docs, setDocs] = useState([]);
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 5;

  const fetchDocs = async () => {
    try {
      const res = await api.get("/documents", {
        params: { skip: page * limit, limit },
      });
      setDocs(res.data.documents);
      setTotal(res.data.total);
    } catch {
      console.error("Failed to fetch documents");
    }
  };

  useEffect(() => {
    fetchDocs();
  }, [page]);

  const totalPages = Math.ceil(total / limit);

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

      {/* Pagination */}
      <div className="flex justify-between mt-4">
        <button
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          disabled={page === 0}
          className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
        >
          Prev
        </button>
        <span>
          Page {page + 1} of {totalPages}
        </span>
        <button
          onClick={() => setPage((p) => (p + 1 < totalPages ? p + 1 : p))}
          disabled={page + 1 >= totalPages}
          className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}
