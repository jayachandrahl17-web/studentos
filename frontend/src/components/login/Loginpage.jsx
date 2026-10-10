
import React, { useState } from "react";

export default function Loginpage({ onAuthenticate, authError = "" }) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const cleanEmail = email.trim();

    if (!cleanEmail || !password) {
      setError("Please enter your email and password.");
      return;
    }

    setIsLoading(true);

    try {
      // Temporary UI flow.
      // Replace this with Django authentication later.
      await onAuthenticate(
        isRegistering
          ? { name: name.trim(), email: cleanEmail, password }
          : { email: cleanEmail, password },
        isRegistering
      );
    } catch (err) {
      setError(
        err?.message || "Unable to sign in. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen min-h-[100dvh] items-center justify-center bg-slate-950 px-4 py-8 text-white sm:px-6 sm:py-12">
      <div className="w-full max-w-md">
        {/* Brand */}
        <header className="mb-8 text-center sm:mb-10">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-500 text-2xl font-bold shadow-lg shadow-indigo-500/30">
            S
          </div>

          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Studyverse
          </h1>

          <p className="mx-auto mt-3 max-w-xs text-sm leading-6 text-slate-400 sm:text-base">
            Your space to focus, learn, and grow.
          </p>
        </header>

        {/* Login Card */}
        <section className="rounded-2xl border border-white/10 bg-slate-900 p-5 shadow-2xl sm:rounded-3xl sm:p-8">
          <h2 className="text-xl font-semibold sm:text-2xl">
            {isRegistering ? "Create your account" : "Welcome back"}
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-400">
            {isRegistering ? "Start your personal Studyverse." : "Sign in to continue your learning journey."}
          </p>

          <form
            onSubmit={handleSubmit}
            className="mt-7 space-y-5 sm:mt-8"
          >
            {isRegistering && (
              <div>
                <label htmlFor="register-name" className="mb-2 block text-sm font-medium text-slate-200">Your name</label>
                <input
                  id="register-name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  required
                  disabled={isLoading}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3.5 text-base outline-none transition placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 disabled:opacity-60 sm:text-sm"
                />
              </div>
            )}
            {/* Email */}
            <div>
              <label
                htmlFor="login-email"
                className="mb-2 block text-sm font-medium text-slate-200"
              >
                Email address
              </label>

              <input
                id="login-email"
                name="email"
                type="email"
                autoComplete="email"
                inputMode="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setError("");
                }}
                required
                disabled={isLoading}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3.5 text-base outline-none transition placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 disabled:opacity-60 sm:text-sm"
              />
            </div>

            {/* Password */}
            <div>
              <div className="mb-2 flex items-center justify-between gap-3">
                <label
                  htmlFor="login-password"
                  className="text-sm font-medium text-slate-200"
                >
                  Password
                </label>

                <button
                  type="button"
                  onClick={() => setShowPassword((current) => !current)}
                  aria-controls="login-password"
                  aria-pressed={showPassword}
                  className="min-h-8 rounded-md text-xs font-medium text-indigo-400 hover:text-indigo-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  {showPassword ? "Hide password" : "Show password"}
                </button>
              </div>

              <input
                id="login-password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError("");
                }}
                required
                disabled={isLoading}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3.5 text-base outline-none transition placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 disabled:opacity-60 sm:text-sm"
              />
            </div>

            {/* Error Message */}
            {(error || authError) && (
              <p
                role="alert"
                className="rounded-xl border border-red-500/20 bg-red-500/10 px-3 py-3 text-sm leading-5 text-red-300"
              >
                {error || authError}
              </p>
            )}

            {/* Forgot Password */}
            {!isRegistering && <div className="text-right text-xs text-slate-500">Use the email address linked to your account.</div>}

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="flex min-h-12 w-full items-center justify-center rounded-xl bg-indigo-500 px-4 py-3 font-semibold text-white transition hover:bg-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-slate-900 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading ? (isRegistering ? "Creating account..." : "Signing in...") : (isRegistering ? "Create account" : "Sign in")}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-slate-400">
            {isRegistering ? "Already have an account?" : "New to Studyverse?"}{" "}
            <button
              type="button"
              onClick={() => {
                setIsRegistering((value) => !value);
                setError("");
              }}
              className="font-semibold text-indigo-400 hover:text-indigo-300"
            >
              {isRegistering ? "Sign in" : "Create an account"}
            </button>
          </p>

          <div className="my-6 flex items-center gap-4">
            <div className="h-px flex-1 bg-slate-800" />

            <span className="whitespace-nowrap text-[10px] font-medium tracking-[0.2em] text-slate-500 sm:text-xs">
              STUDY SMARTER
            </span>

            <div className="h-px flex-1 bg-slate-800" />
          </div>

          <p className="text-center text-xs leading-5 text-slate-500 sm:text-sm">
            Your goals. Your progress. Your Studyverse.
          </p>
        </section>

        <footer className="mt-6 px-2 text-center text-xs text-slate-500">
          © {new Date().getFullYear()} Studyverse. Keep learning.
        </footer>
      </div>
    </main>
  );
}
