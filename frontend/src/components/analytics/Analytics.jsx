import { useEffect, useState } from "react";
import { getAnalytics } from "../../services/api";
import StatCard from "../common/StatCard";

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getAnalytics()
      .then(setData)
      .catch((requestError) => setError(requestError.message || "Could not load analytics."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-extrabold">Analytics</h1>
        <p className="mt-1 text-sm text-slate-500">
          Your academic numbers calculated from backend data.
        </p>
      </div>

      {loading && <p className="text-sm text-slate-500">Loading your analytics...</p>}
      {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</p>}
      {data && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard title="Study time" value={`${data.study_minutes} min`} description="Last 7 days" />
          <StatCard title="Quiz accuracy" value={`${data.quiz_accuracy}%`} description="Last 7 days" />
          <StatCard title="Topic mastery" value={`${data.topic_mastery}%`} description="Your tracked topics" />
          <StatCard title="Subjects" value={data.subjects} description="Current semester" />
        </div>
      )}
    </div>
  );
}
