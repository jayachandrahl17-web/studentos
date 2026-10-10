import { useState } from "react";
import { askAI } from "../../services/api";

const quickPrompts = [
  "What should I study today?",
  "What are my weakest topics?",
  "Why did StudyOS choose today's plan?",
  "Quiz me on my highest-priority topic.",
  "Which topics have the most repeated PYQs?",
  "Teach me one topic from today's plan.",
];

export default function AIAssistant() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  async function sendMessage(event, forcedMessage = null) {
    event?.preventDefault();

    const text = (forcedMessage ?? message).trim();
    if (!text || loading) return;

    const nextMessages = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setMessage("");
    setLoading(true);

    try {
      const result = await askAI(text, messages);

      setMessages([
        ...nextMessages,
        {
          role: "assistant",
          content: result.answer || result.response || "I could not produce an answer.",
          aiUsed: Boolean(result.ai_used),
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessages([
        ...nextMessages,
        {
          role: "assistant",
          content:
            "I couldn't reach the StudyOS backend. Make sure Django is running on port 8000.",
          aiUsed: false,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <div className="rounded-3xl bg-slate-950 p-7 text-white">
        <p className="text-xs font-bold uppercase tracking-widest text-indigo-300">
          StudyOS Intelligence
        </p>

        <h1 className="mt-3 text-3xl font-extrabold">
          Your academic coach.
        </h1>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
          Ask StudyOS about your real syllabus, study plan, weak topics,
          repeated PYQs, exam countdown or performance. The assistant uses
          your stored academic data rather than acting like a generic chatbot.
        </p>
      </div>

      <div className="rounded-2xl border bg-white p-5 shadow-sm">
        <p className="text-sm font-bold text-slate-700">Try asking</p>

        <div className="mt-3 flex flex-wrap gap-2">
          {quickPrompts.map((prompt) => (
            <button
              key={prompt}
              type="button"
              onClick={() => sendMessage(null, prompt)}
              disabled={loading}
              className="rounded-full border px-3 py-2 text-left text-xs font-semibold text-slate-700 transition hover:border-indigo-400 hover:bg-indigo-50 disabled:opacity-50"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      <div className="min-h-72 space-y-4">
        {messages.length === 0 && (
          <div className="rounded-2xl border border-dashed bg-white p-8 text-center">
            <div className="text-4xl">🤖</div>
            <h2 className="mt-3 font-extrabold text-slate-900">
              Ask me anything about your studies.
            </h2>
            <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-500">
              I can help decide what to study, teach a syllabus topic, quiz
              you, explain your plan, find weak areas, and use repeated
              questions to focus your preparation.
            </p>
          </div>
        )}

        {messages.map((item, index) => (
          <div
            key={`${item.role}-${index}`}
            className={
              item.role === "user"
                ? "ml-auto max-w-2xl rounded-2xl rounded-br-md bg-indigo-600 p-4 text-sm leading-6 text-white"
                : "max-w-3xl rounded-2xl rounded-bl-md border bg-white p-5 shadow-sm"
            }
          >
            {item.role === "assistant" && (
              <div className="mb-2 flex items-center gap-2">
                <span className="font-extrabold text-slate-900">StudyOS</span>
                <span className="rounded-full bg-indigo-50 px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-indigo-600">
                  {item.aiUsed ? "AI" : "Local"}
                </span>
              </div>
            )}

            <p className="whitespace-pre-wrap">{item.content}</p>
          </div>
        ))}

        {loading && (
          <div className="max-w-3xl rounded-2xl border bg-white p-5 text-sm text-slate-500 shadow-sm">
            StudyOS is thinking about your academic data…
          </div>
        )}
      </div>

      <form
        onSubmit={sendMessage}
        className="sticky bottom-4 rounded-2xl border bg-white p-4 shadow-lg"
      >
        <label className="text-sm font-bold text-slate-800">
          Ask StudyOS
        </label>

        <div className="mt-3 flex gap-2">
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessage(event);
              }
            }}
            placeholder="e.g. Why should I study DSA today?"
            className="min-h-14 flex-1 resize-none rounded-xl border p-3 text-sm outline-none focus:border-indigo-500"
          />

          <button
            type="submit"
            disabled={loading || !message.trim()}
            className="self-end rounded-xl bg-indigo-600 px-5 py-3 text-sm font-bold text-white disabled:opacity-50"
          >
            {loading ? "Thinking…" : "Ask"}
          </button>
        </div>

        <p className="mt-2 text-xs text-slate-400">
          Enter to send · Shift+Enter for a new line
        </p>
      </form>
    </div>
  );
}
