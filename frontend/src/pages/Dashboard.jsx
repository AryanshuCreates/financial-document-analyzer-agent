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
    <div className="max-w-3xl mx-auto mt-12 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-purple-600">
        Your Documents
      </h2>

      {docs.length === 0 ? (
        <p className="text-gray-600">
          No documents found. Upload one to get started.
        </p>
      ) : (
        <ul className="space-y-4">
          {docs.map((d) => (
            <li
              key={d._id}
              className="border border-gray-200 p-4 rounded-lg shadow-sm hover:shadow-md transition"
            >
              <p className="font-semibold text-gray-800">{d.filename}</p>
              <p className="text-sm text-gray-600">Status: {d.status}</p>
              <Link
                to={`/analysis/${d._id}`}
                className="text-purple-600 hover:text-purple-800 font-medium mt-2 inline-block"
              >
                View Results →
              </Link>
            </li>
          ))}
        </ul>
      )}

      {/* Pagination */}
      <div className="flex justify-between items-center mt-6">
        <button
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          disabled={page === 0}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 shadow disabled:opacity-50"
        >
          Prev
        </button>
        <span className="text-gray-700">
          Page {page + 1} of {totalPages || 1}
        </span>
        <button
          onClick={() => setPage((p) => (p + 1 < totalPages ? p + 1 : p))}
          disabled={page + 1 >= totalPages}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 shadow disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}
