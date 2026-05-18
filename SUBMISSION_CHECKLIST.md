# Submission Checklist

## Required

- [ ] Agent link or containerised app is ready.
- [ ] GitHub repository link is ready.
- [ ] Solution paper is 4-8 pages.
- [ ] README is complete.
- [ ] Dockerfile is present.
- [ ] `docker-compose.yml` is present.
- [ ] `.env.example` is present.
- [ ] Tests pass.
- [ ] Evaluation scripts run.
- [ ] No secrets are committed.
- [ ] Sample data is included.
- [ ] Endpoints are documented.
- [ ] Human evaluation rubric is included.

## Before Submission

- [ ] Run tests:

```bash
.venv\Scripts\python.exe -m pytest -q
```

- [ ] Run evaluation:

```bash
.venv\Scripts\python.exe evaluation\evaluate_task_a.py
.venv\Scripts\python.exe evaluation\evaluate_task_b.py
.venv\Scripts\python.exe scripts\tune_recommendation_weights.py
```

- [ ] Run the app locally:

```bash
uvicorn app.main:app --reload
```

- [ ] Verify:
  - `http://localhost:8000`
  - `http://localhost:8000/health`
  - `http://localhost:8000/docs`

- [ ] Verify Docker if available:

```bash
docker compose up --build
```

- [ ] Push latest commit.
- [ ] Export paper to PDF if required.
- [ ] Submit before the deadline.

## Optional Paper Export

If no PDF export tooling is installed, open `papers/solution_paper_draft.md` and export using one of:

- VS Code Markdown PDF extension
- Pandoc
- Google Docs
- GitHub markdown print-to-PDF flow
