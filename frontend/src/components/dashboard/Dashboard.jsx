import { useEffect, useState } from "react";

import { getSubjects, getAIOverview } from "../../services/api";
import ProgressBar from "../common/ProgressBar";
import StatCard from "../common/StatCard";

export default function Dashboard() {
  const [subjects, setSubjects] = useState([]);
  const [ai, setAI] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        // Both requests happen when the dashboard opens.
        const [subjectData, aiData] = await Promise.all([
          getSubjects(),
          getAIOverview(),
        ]);

        setSubjects(subjectData.results || subjectData);
        setAI(aiData);
      } catch (err) {
        console.error(err);
        setError(
          "Backend is not running. Start Django on port 8000 to load real data."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  // If Django is unavailable, the user still gets a clear message
  // instead of a mysterious blank screen.
  if (loading) {
    return <p className="text-slate-500">Loading StudyOS...</p>;
  }

  return (
    <div className="space-y-6">
      <section className="rounded-3xl bg-slate-950 p-7 text-white">
        <p className="text-xs font-bold uppercase tracking-widest text-indigo-300">
          Academic Intelligence
        </p>

        <h1 className="mt-3 max-w-2xl text-3xl font-extrabold">
          Welcome to your StudyOS control center.
        </h1>

        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
          StudyOS combines your syllabus, progress, assessments and study
          activity to decide what deserves your attention next.
        </p>
      </section>

      {error && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          {error}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Subjects"
          value={subjects.length}
          description="Loaded from Django"
        />

        <StatCard
          title="Next CIA"
          value={ai?.next_plan?.next_assessment?.days_left ?? "—"}
          description={
            ai?.next_plan?.next_assessment
              ? `${ai.next_plan.next_assessment.name} days left`
              : "Calendar not configured"
          }
        />

        <StatCard
          title="AI status"
          value={ai ? "Ready" : "Waiting"}
          description="Academic intelligence engine"
        />

        <StatCard
          title="Target"
          value="9.5+"
          description="Your planned SGPA goal"
        />
      </div>

      {ai?.next_plan?.next_assessment && (
        <section className="rounded-2xl border bg-white p-5 shadow-sm">
          <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">
                Next assessment
              </p>
              <h2 className="mt-1 text-lg font-extrabold">
                {ai.next_plan.next_assessment.name}
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                {ai.next_plan.next_assessment.start_date} → {ai.next_plan.next_assessment.end_date}
              </p>
            </div>
            <div className="rounded-xl bg-indigo-50 px-4 py-3 text-center">
              <p className="text-2xl font-black text-indigo-700">
                {ai.next_plan.next_assessment.days_left}
              </p>
              <p className="text-[11px] font-bold uppercase tracking-widest text-indigo-500">
                days left
              </p>
            </div>
          </div>
        </section>
      )}

      <div className="rounded-2xl border bg-white shadow-sm">
        <div className="border-b p-5">
          <h2 className="font-extrabold">Your subjects</h2>
          <p className="mt-1 text-xs text-slate-400">
            These come from the backend database.
          </p>
        </div>

        <div className="divide-y">
          {subjects.map((subject) => (
            <div key={subject.id} className="p-5">
              <div className="flex justify-between gap-4">
                <div>
                  <h3 className="text-sm font-bold">{subject.name}</h3>
                  <p className="mt-1 text-xs text-slate-400">
                    {subject.code} · {subject.credits} credits
                  </p>
                </div>

                <span className="text-xs font-bold text-indigo-600">
                  {subject.progress ?? 0}%
                </span>
              </div>

              <div className="mt-3">
                <ProgressBar value={subject.progress ?? 0} />
              </div>
            </div>
          ))}

          {subjects.length === 0 && (
            <p className="p-5 text-sm text-slate-400">
              No subjects found. Run the backend seed command first.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
