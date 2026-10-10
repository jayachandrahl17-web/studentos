import { useEffect, useState } from "react";
import {
  completeTopic,
  getSubjectDetail,
  getSubjects,
} from "../../services/api";
import ProgressBar from "../common/ProgressBar";

export default function Subjects() {
  const [subjects, setSubjects] = useState([]);
  const [loadingSubjects, setLoadingSubjects] = useState(true);
  const [subjectsError, setSubjectsError] = useState("");
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState("");
  const [savingTopicId, setSavingTopicId] = useState(null);

  useEffect(() => {
    loadSubjects();
  }, []);

  async function loadSubjects() {
    setLoadingSubjects(true);
    setSubjectsError("");
    try {
      const data = await getSubjects();
      setSubjects(data.results || data);
    } catch (error) {
      console.error("Could not load subjects:", error);
      setSubjectsError(error.message || "Could not load subjects.");
    } finally {
      setLoadingSubjects(false);
    }
  }

  // Clicking a subject now loads its real modules/topics from Django.
  async function handleSelect(subject) {
    setSelected(subject);
    setDetail(null);
    setDetailError("");
    setLoadingDetail(true);

    try {
      const data = await getSubjectDetail(subject.id);
      setDetail(data);
    } catch (error) {
      console.error("Could not load subject syllabus:", error);
      setDetailError("Could not load the syllabus for this subject.");
    } finally {
      setLoadingDetail(false);
    }
  }

  async function handleTopicToggle(topic) {
    const newCompleted = !topic.completed;
    setSavingTopicId(topic.id);

    try {
      await completeTopic(topic.id, newCompleted);

      // Update the open syllabus immediately.
      setDetail((current) => {
        if (!current) return current;

        return {
          ...current,
          modules: current.modules.map((module) => ({
            ...module,
            topics: (module.topics || []).map((item) =>
              item.id === topic.id
                ? { ...item, completed: newCompleted }
                : item
            ),
          })),
        };
      });

      // Refresh the subject card progress as well.
      await loadSubjects();
    } catch (error) {
      console.error("Could not update topic:", error);
      alert("Could not save the topic status. Please try again.");
    } finally {
      setSavingTopicId(null);
    }
  }

  function getModuleProgress(module) {
    const topics = module.topics || [];
    if (!topics.length) return 0;
    const completed = topics.filter((topic) => topic.completed).length;
    return Math.round((completed / topics.length) * 100);
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-extrabold">My Subjects</h1>
        <p className="mt-1 text-sm text-slate-500">
          Select a subject to see every module and syllabus topic.
        </p>
      </div>

      {loadingSubjects && <p className="text-sm text-slate-500">Loading your subjects...</p>}
      {subjectsError && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{subjectsError}</p>}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {subjects.map((subject) => (
          <button
            key={subject.id}
            onClick={() => handleSelect(subject)}
            className="rounded-2xl border bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <p className="text-xs font-bold uppercase text-indigo-600">
              {subject.code}
            </p>

            <h2 className="mt-2 min-h-12 font-extrabold">{subject.name}</h2>

            <p className="mt-2 text-xs text-slate-400">
              {subject.credits} credit{subject.credits === 1 ? "" : "s"}
            </p>

            <div className="mt-5">
              <ProgressBar value={subject.progress ?? 0} />
            </div>

            <p className="mt-2 text-right text-xs font-bold text-slate-500">
              {subject.progress ?? 0}% complete
            </p>
          </button>
        ))}
      </div>

      {selected && (
        <div className="rounded-2xl border bg-indigo-50 p-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase text-indigo-600">
                {selected.code}
              </p>
              <h2 className="mt-1 text-xl font-extrabold">{selected.name}</h2>
              <p className="mt-1 text-sm text-slate-600">
                {selected.credits} credit{selected.credits === 1 ? "" : "s"}
                {detail?.topic_count != null
                  ? ` · ${detail.topic_count} topics`
                  : ""}
              </p>
            </div>

            <button
              onClick={() => {
                setSelected(null);
                setDetail(null);
              }}
              className="rounded-lg bg-slate-900 px-3 py-2 text-xs font-bold text-white"
            >
              Close
            </button>
          </div>

          {loadingDetail && (
            <div className="mt-5 rounded-xl bg-white p-4 text-sm text-slate-500">
              Loading the GAT syllabus...
            </div>
          )}

          {detailError && (
            <div className="mt-5 rounded-xl bg-red-50 p-4 text-sm text-red-700">
              {detailError}
            </div>
          )}

          {detail && !loadingDetail && (
            <div className="mt-5 space-y-4">
              {(detail.modules || []).map((module) => {
                const moduleProgress = getModuleProgress(module);

                return (
                  <section
                    key={module.id}
                    className="overflow-hidden rounded-2xl border bg-white"
                  >
                    <div className="border-b p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <h3 className="font-extrabold">
                            Module {module.number}
                            {module.name && module.name !== `Module ${module.number}`
                              ? ` — ${module.name}`
                              : ""}
                          </h3>
                          <p className="mt-1 text-xs text-slate-400">
                            {module.completed_topics || 0}/
                            {module.topic_count || 0} topics completed
                          </p>
                        </div>

                        <span className="text-xs font-bold text-indigo-600">
                          {moduleProgress}%
                        </span>
                      </div>
                    </div>

                    <div className="divide-y">
                      {(module.topics || []).map((topic) => (
                        <button
                          key={topic.id}
                          type="button"
                          onClick={() => handleTopicToggle(topic)}
                          disabled={savingTopicId === topic.id}
                          className="flex w-full items-center gap-3 px-4 py-3 text-left transition hover:bg-slate-50 disabled:opacity-60"
                          title={
                            topic.completed
                              ? "Mark as not completed"
                              : "Mark as completed"
                          }
                        >
                          <span
                            className={`grid h-5 w-5 shrink-0 place-items-center rounded border-2 text-xs font-black ${
                              topic.completed
                                ? "border-indigo-600 bg-indigo-600 text-white"
                                : "border-slate-300 bg-white text-transparent"
                            }`}
                          >
                            ✓
                          </span>

                          <span
                            className={`text-sm ${
                              topic.completed
                                ? "font-medium text-slate-400 line-through"
                                : "font-semibold text-slate-700"
                            }`}
                          >
                            {topic.name}
                          </span>
                        </button>
                      ))}

                      {(module.topics || []).length === 0 && (
                        <p className="p-4 text-sm text-slate-400">
                          Detailed syllabus topics are not available for this
                          module yet.
                        </p>
                      )}
                    </div>
                  </section>
                );
              })}

              {(detail.modules || []).length === 0 && (
                <div className="rounded-xl bg-amber-50 p-4 text-sm text-amber-800">
                  GAT has not yet provided the detailed module syllabus for this
                  subject in the official source we imported.
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
