import json
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand
from apps.academics.models import Semester


class Command(BaseCommand):
    help = 'Load the current GAT semester planning dates from calendar/semester3.json.'

    def handle(self, *args, **options):
        project_root = Path(__file__).resolve().parents[5]
        calendar_file = project_root / 'calendar' / 'semester3.json'
        with calendar_file.open('r', encoding='utf-8') as f:
            data = json.load(f)

        dates = data['dates']
        semester, _ = Semester.objects.get_or_create(
            number=data['semester'],
            defaults={
                'name': f"Semester {data['semester']}",
                'academic_year': data.get('academic_year', '2026-27'),
            },
        )
        semester.name = f"Semester {data['semester']}"
        semester.academic_year = data.get('academic_year', semester.academic_year)
        semester.start_date = date.fromisoformat(dates['semester_start'])
        semester.cia1_start_date = date.fromisoformat(dates['cia1_start'])
        semester.cia1_end_date = date.fromisoformat(dates['cia1_end'])
        semester.cia2_start_date = date.fromisoformat(dates['cia2_start'])
        semester.cia2_end_date = date.fromisoformat(dates['cia2_end'])
        semester.end_date = date.fromisoformat(dates['semester_end'])
        semester.see_start_date = date.fromisoformat(dates['see_start'])
        semester.save()

        self.stdout.write(self.style.SUCCESS('GAT semester planning calendar loaded successfully.'))
