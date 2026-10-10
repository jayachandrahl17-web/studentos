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

Copy `backend/.env.example` to `backend/.env` and set:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.6-luna
```

Never put the API key in the React frontend. Restart Django after changing `.env`.

If no API key is configured, the Assistant continues to work with a local rule-based fallback.
