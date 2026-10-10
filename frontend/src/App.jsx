
import { useEffect, useState } from "react";
import { getSession, login, logout, register } from "./services/api";

import Header from "./components/layout/Header";
import Sidebar from "./components/layout/Sidebar";

import Dashboard from "./components/dashboard/Dashboard";
import Subjects from "./components/subjects/Subjects";
import StudyPlan from "./components/study/StudyPlan";
import Assessments from "./components/assessments/Assessments";
import Analytics from "./components/analytics/Analytics";
import AIAssistant from "./components/ai/AIAssistant";
import Loginpage from "./components/login/Loginpage";

// ============================================================
// PAGE TITLES
// ============================================================

const pageTitles = {
  dashboard: "Dashboard",
  subjects: "My Subjects",
  study: "Study Plan",
  assessments: "Assessments",
  analytics: "Analytics",
  ai: "AI Assistant",
};

// ============================================================
// MAIN APP
// ============================================================

export default function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [authError, setAuthError] = useState("");
  const [page, setPage] = useState("dashboard");
  const [mobileMenu, setMobileMenu] = useState(false);

  useEffect(() => {
    getSession()
      .then(({ user: currentUser }) => setUser(currentUser))
      .catch((error) => {
        setUser(null);
        if (!error.status || error.status >= 500) setAuthError(error.message);
      })
      .finally(() => setAuthLoading(false));
  }, []);

  async function handleAuthenticate(credentials, isRegistration) {
    setAuthError("");
    try {
      const response = isRegistration
        ? await register(credentials)
        : await login(credentials);
      setUser(response.user);
    } catch (error) {
      setAuthError(error.message || "Unable to authenticate. Please try again.");
      throw error;
    }
  }

  async function handleLogout() {
    try {
      await logout();
    } catch (error) {
      setAuthError(error.message);
      return;
    }
    setUser(null);
    setPage("dashboard");
    setMobileMenu(false);
  }

  // Decide which page to display.
  function renderPage() {
    switch (page) {
      case "subjects":
        return <Subjects />;

      case "study":
        return <StudyPlan />;

      case "assessments":
        return <Assessments />;

      case "analytics":
        return <Analytics />;

      case "ai":
        return <AIAssistant />;

      case "dashboard":
      default:
        return <Dashboard />;
    }
  }

  if (authLoading) {
    return <main className="grid min-h-screen place-items-center text-sm text-slate-500">Restoring your Studyverse session...</main>;
  }

  if (!user) {
    return <Loginpage onAuthenticate={handleAuthenticate} authError={authError} />;
  }

  // Main StudyOS application
  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar page={page} setPage={setPage} />

      {/* Mobile navigation menu */}
      {mobileMenu && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/40 lg:hidden"
          onClick={() => setMobileMenu(false)}
        >
          <div
            className="h-full w-64 max-w-[85vw] overflow-y-auto bg-slate-950 p-5 text-white"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-xl font-extrabold">StudyOS</h2>

              <button
                type="button"
                onClick={() => setMobileMenu(false)}
                aria-label="Close navigation menu"
                className="rounded-lg px-3 py-2 text-slate-300 hover:bg-white/10"
              >
                ✕
              </button>
            </div>

            <nav className="space-y-1">
              {Object.entries(pageTitles).map(([id, title]) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => {
                    setPage(id);
                    setMobileMenu(false);
                  }}
                  className={`block w-full rounded-lg px-3 py-3 text-left text-sm transition ${
                    page === id
                      ? "bg-indigo-500 text-white"
                      : "text-slate-300 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  {title}
                </button>
              ))}
            </nav>
          </div>
        </div>
      )}

      <Header
        title={pageTitles[page]}
        user={user}
        onMenuClick={() => setMobileMenu(true)}
        onLogout={handleLogout}
      />

      <main className="px-4 py-6 sm:px-5 md:px-6 lg:ml-60">
        <div className="mx-auto w-full max-w-6xl">
          {authError && (
            <p role="alert" className="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {authError}
            </p>
          )}
          {renderPage()}
        </div>
      </main>
    </div>
  );
}