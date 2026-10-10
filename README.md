# StudyOS — Academic Intelligence

StudyOS is a React + Tailwind + Django REST academic planning application for Semester 3 ISE.

## Current working features

- Verified GAT Semester 3 syllabus imported into Django.
- Real module/topic names and topic completion tracking.
- Semester 3 academic planning dates from the supplied GAT 2026–27 calendar.
- CIA-1, CIA-2, semester-end and SEE countdowns.
- Adaptive weekly study planner with a maximum of two subjects per study day.
- Four- or five-day weekly study setting.
- Credit-aware scheduling: subjects with 3+ credits are targeted twice weekly; 1-credit subjects are targeted once when capacity permits.
- Explicit constraint reporting when the requested weekly minimums cannot all fit inside the two-subject/five-day limit.
- Topic priority based on mastery/weakness, PYQ frequency, importance, urgency, revision freshness and credits.
- Daily topic tasks with PYQ practice guidance.
- Completing a Study Plan task updates the same syllabus topic and recalculates the next plan.
- Optional OpenAI ranking layer for supplied syllabus topics and past-question signals.
- Existing assessments, marks, quiz, revision, analytics and AI assistant APIs remain available.

## Important planning rule

The current Semester 3 structure has five subjects at 3+ credits and two 1-credit subjects. Five study days × two subjects/day provides ten subject slots, while the requested minimums require twelve. StudyOS therefore protects the high-credit twice-weekly minimums and reports/rotates lower-credit overflow rather than silently scheduling a third subject on a day.

## Backend setup

```bash
cd backend-2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py import_syllabus
python manage.py import_calendar
python manage.py runserver
```

Django uses SQLite when `DB_NAME` is empty. PostgreSQL can be enabled through `.env`.

## Production Deployment

The Django project lives in `backend-2/` and uses `config.wsgi:application`. The React app lives in `frontend/` and uses Vite.

### Render backend

1. Connect this GitHub repository to Render and create a Blueprint from `render.yaml`.
2. Review the selected Render plans and pricing. The Blueprint provisions a PostgreSQL database and a Starter web service.
3. Set `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` on the Render service to the exact production Vercel origin, for example `https://studentos.vercel.app` (no trailing slash).
4. Keep the generated `SECRET_KEY`, `DEBUG=false`, and the Blueprint-provided `DATABASE_URL`. Render sets `RENDER_EXTERNAL_HOSTNAME`, which Django adds to `ALLOWED_HOSTS`.
5. Render installs `backend-2/requirements.txt`, collects static files with `backend-2/build.sh`, runs migrations before deploy, and starts `config.wsgi:application` with Gunicorn.

### Vercel frontend

1. Import the same repository into Vercel and set the project Root Directory to `frontend`.
2. Use the Vite framework preset, build command `npm run build`, and output directory `dist` (also specified in `frontend/vercel.json`).
3. Add `VITE_API_BASE_URL=https://<your-render-service>.onrender.com` as a Vercel environment variable for Production, then redeploy.
4. Copy the final Vercel production origin into both Render origin variables above. Because authentication uses Django sessions and CSRF cookies across Render/Vercel origins, production defaults to secure cookies with `SameSite=None` and credentialed CORS.

The API URL is public configuration, not a secret. Never add the Django secret, database URL, or AI provider key to Vercel. Keep those only in Render environment settings. `frontend/.env.example` and `backend-2/.env.example` contain placeholders for local setup.

## OpenAI (optional but recommended)

Keep the API key on Django, never in React:

```text
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-5.6-luna
```

Without a key, the deterministic StudyOS planner still works. With a key, OpenAI can rerank already-known topics using PYQ frequency, mastery, importance and urgency. It cannot invent syllabus topics or dates.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Current semester calendar

The included Semester 3 planning data is:

- Semester starts: 2026-09-07
- CIA-1: 2026-10-26 to 2026-10-30
- CIA-2: 2026-12-12 to 2026-12-18
- CIE freeze / last working day: 2026-12-26
- SEE commencement: 2026-12-31

When GAT publishes the next semester's official calendar, update the semester calendar data rather than guessing future dates.


## AI Assistant

The AI Assistant is a StudyOS academic coach, not a generic chatbot.

When `OPENAI_API_KEY` is configured on the Django backend, it can use a compact snapshot of:
- the current semester and next assessment window
- subject credits and progress
- unfinished topics and mastery
- PYQ/repetition frequency
- the current deterministic study plan
- StudyOS weekly scheduling constraints

It can explain the plan, recommend stored topics, teach syllabus topics, create practice questions, discuss weak areas, and analyze repeated-question priorities.

The deterministic planner remains responsible for hard constraints and academic arithmetic. OpenAI is used for language, explanation and reasoning over StudyOS data.

### Enable OpenAI

Copy `backend-2/.env.example` to `backend-2/.env` and set:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.6-luna
```

Never put the API key in the React frontend. Restart Django after changing `.env`.

If no API key is configured, the Assistant continues to work with a local rule-based fallback.
