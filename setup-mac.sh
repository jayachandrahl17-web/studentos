#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/backend-2"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
python manage.py migrate
python manage.py import_syllabus
python manage.py import_calendar
printf '\nBackend ready. Start it with:\n  cd backend-2 && source venv/bin/activate && python manage.py runserver\n'
