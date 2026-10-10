from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Load StudyOS Semester 3 with the verified GAT syllabus."

    def handle(self, *args, **kwargs):
        call_command("import_syllabus")
        self.stdout.write(
            self.style.SUCCESS("StudyOS Semester 3 seed completed using the verified GAT syllabus.")
        )
