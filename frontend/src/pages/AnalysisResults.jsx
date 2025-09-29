import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";

export default function AnalysisResults() {
  const { documentId } = useParams();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAnalysis = async () => {
    try {
      const res = await api.get(`/analyses/${documentId}`);
      setAnalyses(res.data);
    } catch {
      console.error("Failed to fetch analysis");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
    const interval = setInterval(fetchAnalysis, 5000); // poll
    return () => clearInterval(interval);
  }, [documentId]);

  if (loading) return <p className="p-6">Loading...</p>;

  return (
    <div className="max-w-3xl mx-auto mt-12 space-y-6">
      <h2 className="text-2xl font-bold">Analysis Results</h2>
      {analyses.length === 0 && (
        <p className="text-gray-600">No results yet. Try again later.</p>
      )}
      {analyses.map((a) => (
        <div key={a._id} className="border p-4 rounded bg-white shadow">
          <p>
            <strong>Status:</strong> {a.status}
          </p>
          {a.local_summary && (
            <div className="mt-2">
              <h3 className="font-semibold">Local Summary:</h3>
              <p>{a.local_summary.summary}</p>
              <p className="text-sm text-gray-500">
                Confidence: {a.local_summary.confidence}
              </p>
            </div>
          )}
          {a.crew_result && (
            <div className="mt-2">
              <h3 className="font-semibold">CrewAI Result:</h3>
              <pre className="whitespace-pre-wrap bg-gray-100 p-2 rounded text-sm">
                {JSON.stringify(a.crew_result, null, 2)}
              </pre>
            </div>
          )}
          {a.error && <p className="text-red-600 mt-2">Error: {a.error}</p>}
        </div>
      ))}
    </div>
  );
}
