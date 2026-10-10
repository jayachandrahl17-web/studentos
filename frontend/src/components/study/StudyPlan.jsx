import { useEffect, useState } from "react";
import { completeTopic, createStudySession, getStudyPlan } from "../../services/api";

function formatDate(value) {
  return new Intl.DateTimeFormat("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "short",
  }).format(new Date(`${value}T00:00:00`));
}

export default function StudyPlan() {
  const [plan, setPlan] = useState(null);
  const [minutes, setMinutes] = useState(180);
  const [days, setDays] = useState(5);
  const [loading, setLoading] = useState(true);
  const [savingTopicId, setSavingTopicId] = useState(null);
  const [loggingTopicId, setLoggingTopicId] = useState(null);
  const [sessionMinutes, setSessionMinutes] = useState(30);
  const [sessionNotes, setSessionNotes] = useState("");
  const [savingSession, setSavingSession] = useState(false);
  const [sessionMessage, setSessionMessage] = useState("");
  const [error, setError] = useState("");

  async function loadPlan() {
    setLoading(true);
    setError("");
    try {
      const data = await getStudyPlan({ minutes, days, ai: true });
      setPlan(data);
    } catch (err) {
      console.error(err);
      setError("Could not load the StudyOS planning engine.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPlan();
  }, [minutes, days]);

  async function markCompleted(topicId) {
    setSavingTopicId(topicId);
    try {
      await completeTopic(topicId, true);
      await loadPlan();
    } catch (err) {
      console.error(err);
      setError("Could not update the topic. Please try again.");
    } finally {
      setSavingTopicId(null);
    }
  }

  async function logSession(event, topicId) {
    event.preventDefault();
    setSavingSession(true);
    setError("");
    setSessionMessage("");
    try {
      await createStudySession({
        topic: topicId,
        minutes: Number(sessionMinutes),
        notes: sessionNotes.trim(),
      });
      setSessionMessage("Study session saved to your account.");
      setLoggingTopicId(null);
      setSessionNotes("");
    } catch (requestError) {
      setError(requestError.message || "Could not save the study session.");
    } finally {
      setSavingSession(false);
    }
  }

  const today = plan?.today;
  const assessment = plan?.next_assessment;
  const conflict = plan?.constraint_status?.constraint_conflict;

  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">
            Adaptive planner
          </p>
          <h1 className="mt-2 text-2xl font-extrabold">Today's Study Plan</h1>
          <p className="mt-1 text-sm text-slate-500">
            StudyOS combines exam urgency, credits, mastery, syllabus importance and PYQ frequency.
          </p>
        </div>
        <div className="flex gap-2">
          <label className="rounded-xl border bg-white px-3 py-2 text-xs font-bold text-slate-600">
            Minutes/day
            <select
              value={minutes}
              onChange={(e) => setMinutes(Number(e.target.value))}
              className="ml-2 rounded border-0 bg-slate-50 px-2 py-1 font-bold outline-none"
            >
              <option value={120}>120</option>
              <option value={150}>150</option>
              <option value={180}>180</option>
              <option value={210}>210</option>
              <option value={240}>240</option>
            </select>
          </label>
          <label className="rounded-xl border bg-white px-3 py-2 text-xs font-bold text-slate-600">
            Study days
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="ml-2 rounded border-0 bg-slate-50 px-2 py-1 font-bold outline-none"
            >
              <option value={4}>4</option>
              <option value={5}>5</option>
            </select>
          </label>
        </div>
      </div>

      {error && <div className="rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div>}
      {sessionMessage && <p role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{sessionMessage}</p>}

      {assessment && (
        <section className="rounded-3xl bg-slate-950 p-6 text-white shadow-sm">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-indigo-300">Next assessment</p>
              <h2 className="mt-2 text-2xl font-extrabold">{assessment.name}</h2>
              <p className="mt-1 text-sm text-slate-300">
                {assessment.start_date} → {assessment.end_date}
              </p>
            </div>
            <div className="rounded-2xl bg-white/10 px-5 py-4 text-center">
              <p className="text-3xl font-black">{assessment.days_left}</p>
              <p className="text-xs font-bold uppercase tracking-widest text-slate-300">days left</p>
            </div>
          </div>
        </section>
      )}

      {conflict && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <p className="font-extrabold">Your weekly rules have a capacity conflict.</p>
          <p className="mt-1">
            {plan.constraint_status.requested_subject_sessions} subject sessions are requested, but {plan.constraint_status.available_subject_slots} fit into {days} study days × 2 subjects/day. StudyOS protects the twice-weekly high-credit subjects and reports the 1-credit subjects that overflow instead of breaking your two-subject daily limit.
          </p>
          {plan.constraint_status.overflow_low_credit_subjects?.length > 0 && (
            <p className="mt-2 text-xs font-semibold">
              Lower-credit overflow: {plan.constraint_status.overflow_low_credit_subjects.join(", ")}.
            </p>
          )}
        </div>
      )}

      <section className="rounded-2xl border bg-white shadow-sm">
        <div className="border-b p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="font-extrabold">Today</h2>
              <p className="mt-1 text-xs text-slate-400">{today ? formatDate(today.date) : ""}</p>
            </div>
            {plan?.ai_used && (
              <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold text-indigo-700">AI ranked</span>
            )}
          </div>
        </div>

        {loading && <p className="p-5 text-sm text-slate-500">Calculating your plan...</p>}

        {!loading && today?.rest_day && (
          <div className="p-5">
            <p className="font-bold">Today is a planned rest day.</p>
            <p className="mt-1 text-sm text-slate-500">
              Your next study day is {today.next_study_day ? formatDate(today.next_study_day) : "not available"}.
            </p>
          </div>
        )}

        {!loading && !today?.rest_day && (
          <div className="divide-y">
            {(today?.subjects || []).map((subject) => (
              <div key={subject.subject_id} className="p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-bold uppercase text-indigo-600">{subject.code}</p>
                    <h3 className="mt-1 font-extrabold">{subject.subject}</h3>
                  </div>
                  <span className="text-xs font-bold text-slate-400">{subject.minutes} min</span>
                </div>
                <div className="mt-4 space-y-3">
                  {subject.tasks.map((task) => (
                    <div key={task.topic_id} className="rounded-xl border bg-slate-50 p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="text-sm font-bold text-slate-800">{task.topic}</p>
                          <p className="mt-1 text-xs text-slate-500">
                            Module {task.module} · {task.minutes} min · priority {task.priority}
                          </p>
                          <p className="mt-2 text-xs text-slate-600">{task.ai_reason || task.reason}</p>
                          <p className="mt-2 text-xs font-semibold text-indigo-700">{task.practice_note}</p>
                          {task.questions?.length > 0 && (
                            <div className="mt-3 rounded-lg bg-white p-3">
                              <p className="text-[11px] font-bold uppercase tracking-wide text-slate-400">Repeated questions</p>
                              <ul className="mt-2 list-disc space-y-1 pl-4 text-xs text-slate-600">
                                {task.questions.map((question, index) => (
                                  <li key={index}>{question}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                        <div className="flex shrink-0 flex-col gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              setLoggingTopicId(loggingTopicId === task.topic_id ? null : task.topic_id);
                              setSessionMinutes(task.minutes);
                              setSessionMessage("");
                            }}
                            className="rounded-lg border bg-white px-3 py-2 text-xs font-bold text-slate-700"
                          >
                            Log session
                          </button>
                          <button
                            type="button"
                            onClick={() => markCompleted(task.topic_id)}
                            disabled={savingTopicId === task.topic_id}
                            className="rounded-lg bg-indigo-600 px-3 py-2 text-xs font-bold text-white disabled:opacity-50"
                          >
                            {savingTopicId === task.topic_id ? "Saving…" : "Completed"}
                          </button>
                        </div>
                      </div>
                      {loggingTopicId === task.topic_id && (
                        <form onSubmit={(event) => logSession(event, task.topic_id)} className="mt-4 flex flex-wrap items-end gap-3 border-t pt-4">
                          <label className="text-xs font-semibold text-slate-600">
                            Minutes
                            <input type="number" min="1" max="1440" required value={sessionMinutes} onChange={(event) => setSessionMinutes(event.target.value)} className="mt-1 block w-24 rounded-lg border px-3 py-2 text-sm" />
                          </label>
                          <label className="min-w-48 flex-1 text-xs font-semibold text-slate-600">
                            Notes
                            <input type="text" value={sessionNotes} onChange={(event) => setSessionNotes(event.target.value)} className="mt-1 block w-full rounded-lg border px-3 py-2 text-sm" />
                          </label>
                          <button type="submit" disabled={savingSession} className="rounded-lg bg-slate-900 px-3 py-2.5 text-xs font-bold text-white disabled:opacity-50">
                            {savingSession ? "Saving..." : "Save session"}
                          </button>
                        </form>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="rounded-2xl border bg-white shadow-sm">
        <div className="border-b p-5">
          <h2 className="font-extrabold">This week</h2>
          <p className="mt-1 text-xs text-slate-400">Maximum two subjects on any study day.</p>
        </div>
        <div className="divide-y">
          {(plan?.week || []).map((day) => (
            <div key={day.date} className="p-5">
              <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
                <div>
                  <p className="font-bold">{day.day}</p>
                  <p className="text-xs text-slate-400">{formatDate(day.date)}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {day.subjects.map((subject) => (
                    <span key={subject.subject_id} className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold text-indigo-700">
                      {subject.subject} · {subject.minutes}m
                    </span>
                  ))}
                  {!day.subjects.length && <span className="text-xs text-slate-400">Rest / no scheduled session</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
