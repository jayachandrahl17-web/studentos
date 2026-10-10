import { Menu } from "lucide-react";

// Simple top bar.
// On phones the menu button opens the mobile navigation.

export default function Header({ title, user, onMenuClick, onLogout }) {
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b bg-white/95 px-4 backdrop-blur md:px-6 lg:ml-60">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="rounded-lg border p-2 lg:hidden"
        >
          <Menu size={18} />
        </button>

        <div>
          <h2 className="font-extrabold text-slate-900">{title}</h2>
          <p className="text-[11px] text-slate-400">
            Semester 3 · ISE · 2026-27
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden text-right sm:block">
          <p className="text-sm font-semibold text-slate-800">{user?.name || user?.email}</p>
          <p className="text-xs text-slate-500">{user?.email}</p>
        </div>
        <div className="grid h-9 w-9 place-items-center rounded-xl bg-indigo-600 text-xs font-bold text-white" aria-hidden="true">
          {(user?.name || user?.email || "S").slice(0, 1).toUpperCase()}
        </div>
        <button
          type="button"
          onClick={onLogout}
          className="rounded-lg border px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
