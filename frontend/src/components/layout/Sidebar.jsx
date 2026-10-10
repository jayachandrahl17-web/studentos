import {
  Activity,
  BarChart3,
  BookOpen,
  BrainCircuit,
  CalendarDays,
  FileText,
  LayoutDashboard,
} from "lucide-react";

// The sidebar only tells App which page the user wants to see.
// We deliberately keep routing simple so a beginner can understand it.

const links = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "subjects", label: "Subjects", icon: BookOpen },
  { id: "study", label: "Study Plan", icon: CalendarDays },
  { id: "assessments", label: "Assessments", icon: FileText },
  { id: "analytics", label: "Analytics", icon: BarChart3 },
  { id: "ai", label: "AI Assistant", icon: BrainCircuit },
];

export default function Sidebar({ page, setPage }) {
  return (
    <aside className="fixed left-0 top-0 hidden h-screen w-60 bg-slate-950 p-5 text-white lg:block">
      <div className="mb-8 flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-600">
          <BrainCircuit size={21} />
        </div>

        <div>
          <h1 className="font-extrabold">StudyOS</h1>
          <p className="text-[10px] text-slate-400">Academic Intelligence</p>
        </div>
      </div>

      <p className="mb-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">
        Main menu
      </p>

      <nav className="space-y-1">
        {links.map((link) => {
          const Icon = link.icon;
          const active = page === link.id;

          return (
            <button
              key={link.id}
              onClick={() => setPage(link.id)}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-semibold ${
                active
                  ? "bg-white text-slate-900"
                  : "text-slate-300 hover:bg-white/10"
              }`}
            >
              <Icon size={17} />
              {link.label}
            </button>
          );
        })}
      </nav>

      <div className="absolute bottom-5 left-5 right-5 rounded-xl border border-white/10 bg-white/5 p-3 text-xs text-slate-400">
        <Activity size={15} className="mb-2 text-indigo-400" />
        Your academic control center.
      </div>
    </aside>
  );
}
