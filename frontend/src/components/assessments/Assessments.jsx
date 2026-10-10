import { useEffect, useState } from "react";
import { createMark, getAssessments, getMarks, getSemester3 } from "../../services/api";

function formatDate(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function daysUntil(value) {
  if (!value) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(`${value}T00:00:00`);
  return Math.ceil((target - today) / 86400000);
}

export default function Assessments() {
  const [semester, setSemester] = useState(null);
  const [assessments, setAssessments] = useState([]);
  const [marks, setMarks] = useState([]);
  const [selectedAssessment, setSelectedAssessment] = useState("");
  const [score, setScore] = useState("");
  const [note, setNote] = useState("");
  const [savingMark, setSavingMark] = useState(false);
  const [markMessage, setMarkMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getSemester3(), getAssessments(), getMarks()])
      .then(([semesterData, assessmentData, markData]) => {
        setSemester(semesterData);
        const rows = assessmentData.results || assessmentData || [];
        setAssessments(rows);
        setMarks(markData.results || markData || []);
        if (rows.length) setSelectedAssessment(String(rows[0].id));
      })
      .catch((err) => {
        console.error(err);
        setError(err.message || "Could not load the academic calendar.");
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleRecordMark(event) {
    event.preventDefault();
    setError("");
    setMarkMessage("");
    setSavingMark(true);
    try {
      const created = await createMark({
        assessment: Number(selectedAssessment),
        score: Number(score),
        note: note.trim(),
      });
      setMarks((current) => [created, ...current]);
      setScore("");
      setNote("");
      setMarkMessage("Mark saved to your account.");
    } catch (requestError) {
      setError(requestError.message || "Could not save this mark.");
    } finally {
      setSavingMark(false);
    }
  }

  const calendar = semester
    ? [
        {
          name: "CIA-1",
          start: semester.cia1_start_date,
          end: semester.cia1_end_date,
          description: "First internal assessment window",
        },
        {
          name: "CIA-2",
          start: semester.cia2_start_date,
          end: semester.cia2_end_date,
          description: "Second internal assessment window",
        },
        {
          name: "Semester end",
          start: semester.end_date,
          end: semester.end_date,
          description: "CIE freeze / last working day",
        },
        {
          name: "SEE",
          start: semester.see_start_date,
          end: semester.see_start_date,
          description: "Semester-end examination commencement",
        },
      ].filter((item) => item.start)
    : [];

  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">
          {semester ? `${semester.name} · ${semester.academic_year}` : "Current semester"}
        </p>
        <h1 className="mt-2 text-2xl font-extrabold">Academic Timeline</h1>
        <p className="mt-1 text-sm text-slate-500">
          StudyOS uses these official semester dates as the planning clock.
        </p>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div>
      )}
      {loading && <p className="text-sm text-slate-500">Loading assessments and marks...</p>}

      <div className="grid gap-4 md:grid-cols-2">
        {calendar.map((item) => {
          const days = daysUntil(item.start);
          const futureDays = calendar
            .map((x) => daysUntil(x.start))
            .filter((value) => value !== null && value >= 0);
          const isNext = days !== null && days >= 0 && days === Math.min(...futureDays);
          return (
            <div key={item.name} className="rounded-2xl border bg-white p-5 shadow-sm">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-bold uppercase text-indigo-600">{item.name}</p>
                  <h2 className="mt-2 text-lg font-extrabold">
                    {formatDate(item.start)}
                    {item.end && item.end !== item.start ? ` – ${formatDate(item.end)}` : ""}
                  </h2>
                  <p className="mt-1 text-sm text-slate-500">{item.description}</p>
                </div>
                {isNext && (
                  <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold text-indigo-700">
                    Next
                  </span>
                )}
              </div>
              {days !== null && (
                <p className="mt-4 text-sm font-bold text-slate-700">
                  {days < 0
                    ? "Completed / past date"
                    : days === 0
                      ? "Today"
                      : `${days} day${days === 1 ? "" : "s"} remaining`}
                </p>
              )}
            </div>
          );
        })}
      </div>

      {assessments.length > 0 && (
        <div className="rounded-2xl border bg-white shadow-sm">
          <div className="border-b p-5">
            <h2 className="font-extrabold">Subject-level assessments</h2>
            <p className="mt-1 text-xs text-slate-400">
              These appear only when actual subject assessment records are added.
            </p>
          </div>
          <div className="divide-y">
            {assessments.map((assessment) => (
              <div key={assessment.id} className="p-5">
                <h3 className="font-bold">{assessment.name}</h3>
                <p className="mt-1 text-xs text-slate-400">
                  {assessment.subject_name || "Subject"} · {formatDate(assessment.date)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {assessments.length > 0 && (
        <section className="rounded-2xl border bg-white shadow-sm">
          <div className="border-b p-5">
            <h2 className="font-extrabold">Your marks</h2>
            <p className="mt-1 text-xs text-slate-400">Marks are private to your account.</p>
          </div>
          <form onSubmit={handleRecordMark} className="grid gap-3 border-b p-5 sm:grid-cols-[minmax(0,1fr)_8rem_minmax(0,1fr)_auto] sm:items-end">
            <label className="text-xs font-semibold text-slate-600">
              Assessment
              <select value={selectedAssessment} onChange={(event) => setSelectedAssessment(event.target.value)} className="mt-1 block w-full rounded-lg border bg-white px-3 py-2 text-sm">
                {assessments.map((assessment) => <option key={assessment.id} value={assessment.id}>{assessment.name} · {assessment.subject_name}</option>)}
              </select>
            </label>
            <label className="text-xs font-semibold text-slate-600">
              Score
              <input type="number" min="0" max={assessments.find((item) => String(item.id) === selectedAssessment)?.max_marks || undefined} step="0.5" value={score} onChange={(event) => setScore(event.target.value)} required className="mt-1 block w-full rounded-lg border px-3 py-2 text-sm" />
            </label>
            <label className="text-xs font-semibold text-slate-600">
              Note
              <input type="text" value={note} onChange={(event) => setNote(event.target.value)} className="mt-1 block w-full rounded-lg border px-3 py-2 text-sm" />
            </label>
            <button type="submit" disabled={savingMark || !selectedAssessment} className="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-bold text-white disabled:opacity-50">
              {savingMark ? "Saving..." : "Save mark"}
            </button>
          </form>
          {markMessage && <p role="status" className="px-5 pt-3 text-sm text-emerald-700">{markMessage}</p>}
          {marks.length ? (
            <div className="divide-y">
              {marks.map((mark) => {
                const assessment = assessments.find((item) => item.id === mark.assessment);
                return (
                  <div key={mark.id} className="flex flex-wrap items-center justify-between gap-2 px-5 py-4">
                    <div>
                      <p className="text-sm font-bold">{assessment?.name || "Assessment"} · {assessment?.subject_name || "Subject"}</p>
                      {mark.note && <p className="mt-1 text-xs text-slate-500">{mark.note}</p>}
                    </div>
                    <p className="text-sm font-extrabold text-indigo-700">{mark.score}{assessment ? ` / ${assessment.max_marks}` : ""}</p>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="p-5 text-sm text-slate-500">No marks recorded yet.</p>
          )}
        </section>
      )}
    </div>
  );
}
