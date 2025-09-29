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
    const interval = setInterval(fetchAnalysis, 5000); // poll every 5s
    return () => clearInterval(interval);
  }, [documentId]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto mt-12 p-6 bg-white rounded-lg shadow-md text-center">
        <p className="text-purple-600 font-medium">Loading...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto mt-12 space-y-6">
      <h2 className="text-2xl font-bold text-purple-600">Analysis Results</h2>

      {analyses.length === 0 && (
        <p className="text-gray-600">
          No results yet. Please check back later.
        </p>
      )}

      {analyses.map((a) => (
        <div
          key={a._id}
          className="border border-gray-200 p-6 rounded-lg bg-white shadow-sm hover:shadow-md transition"
        >
          <p className="text-gray-800">
            <strong className="text-purple-600">Status:</strong> {a.status}
          </p>

          {a.local_summary && (
            <div className="mt-4">
              <h3 className="font-semibold text-purple-600">Local Summary:</h3>
              <p className="text-gray-700">{a.local_summary.summary}</p>
              <p className="text-sm text-gray-500 mt-1">
                Confidence: {a.local_summary.confidence}
              </p>
            </div>
          )}

          {a.crew_result && (
            <div className="mt-4">
              <h3 className="font-semibold text-purple-600">CrewAI Result:</h3>
              <pre className="whitespace-pre-wrap bg-gray-100 p-3 rounded text-sm text-gray-700">
                {JSON.stringify(a.crew_result, null, 2)}
              </pre>
            </div>
          )}

          {a.error && (
            <p className="text-red-600 mt-4 font-medium">Error: {a.error}</p>
          )}
        </div>
      ))}
    </div>
  );
}
