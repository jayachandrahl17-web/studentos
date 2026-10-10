import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.academics.models import Semester, Subject, Module, Topic


class Command(BaseCommand):
    help = "Import the verified Semester 3 syllabus into StudyOS."

    def handle(self, *args, **kwargs):
        project_root = Path(__file__).resolve().parents[5]
        syllabus_file = project_root / "syllabus" / "semester3.json"

        with syllabus_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        with transaction.atomic():
            semester, _ = Semester.objects.get_or_create(
                number=data["semester"],
                defaults={
                    "name": f"Semester {data['semester']}",
                    "academic_year": data.get("academic_year", "2026-27"),
                },
            )

            semester.name = f"Semester {data['semester']}"
            semester.academic_year = data.get("academic_year", semester.academic_year)
            semester.save()

            for subject_data in data["subjects"]:
                subject, _ = Subject.objects.get_or_create(
                    code=subject_data["code"],
                    defaults={
                        "semester": semester,
                        "name": subject_data["name"],
                        "credits": subject_data["credits"],
                        "color": subject_data.get("color", "indigo"),
                    },
                )

                subject.semester = semester
                subject.name = subject_data["name"]
                subject.credits = subject_data["credits"]
                subject.color = subject_data.get("color", subject.color)
                subject.save()

                for module_data in subject_data.get("modules", []):
                    module, _ = Module.objects.get_or_create(
                        subject=subject,
                        number=module_data["number"],
                        defaults={
                            "name": module_data["name"],
                            "estimated_minutes": module_data["hours"] * 60,
                        },
                    )

                    module.name = module_data["name"]
                    module.estimated_minutes = module_data["hours"] * 60
                    module.save()

                    for topic_name in module_data["topics"]:
                        Topic.objects.update_or_create(
                            module=module,
                            name=topic_name,
                            defaults={
                                "estimated_minutes": max(
                                20, round((module_data["hours"] * 60) / max(len(module_data["topics"]), 1))
                                ),
                                "importance": 3,
                            },
                        )

        self.stdout.write(self.style.SUCCESS("Verified GAT Semester 3 syllabus imported."))
        for subject_data in data["subjects"]:
            module_count = len(subject_data.get("modules", []))
            topic_count = sum(len(m["topics"]) for m in subject_data.get("modules", []))
            status = subject_data.get("status", "verified")
            self.stdout.write(
                f"{subject_data['code']}: {module_count} modules, "
                f"{topic_count} topics [{status}]"
            )
