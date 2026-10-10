# StudyOS - Full Stack Academic Intelligence

This project contains BOTH parts of StudyOS:

- `frontend/` -> React + Tailwind
- `backend-2/` -> Django + Django REST Framework + database + AI engine

## Why the frontend is simple

The frontend is intentionally beginner-friendly.

Instead of putting hundreds of lines into one file, the code is separated into:

```text
components/
  common/
  layout/
  dashboard/
  subjects/
  study/
  assessments/
  analytics/
  ai/

services/
  api.js
```

Every important file contains comments explaining what it does.

## Run the backend

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

Backend:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health/
```

## Run the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## How the application works

```text
React
  |
  | fetch()
  v
Django REST API
  |
  v
PostgreSQL
  |
  v
Academic data
  |
  v
AI Engine
  |
  v
Study recommendation
```

## Important

The backend is preserved from the connected StudyOS backend package.

The frontend is deliberately simplified so that you can read it, understand it,
and gradually replace parts yourself while learning React and backend development.
