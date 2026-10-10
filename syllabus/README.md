# StudyOS Semester 3 Syllabus

The `semester3.json` file contains the structured Semester 3 syllabus used by StudyOS.

## Source policy

Academic content is based on Global Academy of Technology (GAT) official documents.

- GAT 2024 Scheme & Syllabus PDF:
  https://www.gat.ac.in/documents/cs_ai_ml/2024%20scheme%20%26%20syllabus.pdf
- GAT 2024-25 ISE Scheme:
  https://www.gat.ac.in/documents/2024-25_Batch_Scheme.pdf

The importer deliberately does **not** invent missing syllabus content.

`BAS24358D — Data Visualization with Python` is included as a Semester 3 subject because the official ISE scheme confirms the course code/title, but its detailed module syllabus was not found in the official GAT documents indexed during this import. It is therefore left without invented topics until the detailed official course PDF is located or supplied.

## Import

From `backend/` with the project's virtual environment active:

```bash
python manage.py import_syllabus
```

The existing command also works:

```bash
python manage.py seed_studyos
```

Both commands use the same verified syllabus dataset.
