# Backend — Game+ Quest League (Fresh MVC Scaffold)

This is a clean MVC-style FastAPI backend scaffold for the Game+ Quest League project.

Structure

- `app/` — application code
  - `controllers/` — HTTP route handlers
  - `models/` — database models (SQLAlchemy)
  - `services/` — business logic (state calculator, quest engine)
  - `schemas/` — Pydantic schemas
  - `db.py`, `main.py`

Quick start (local dev)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Pipeline (CSV-driven prototype)

Use the `app.services.pipeline` module to run the CSV-driven pipeline without a DB.

Database

1. Set `DATABASE_URL` in `backend/.env` to point to your Postgres (Docker) instance (SQLAlchemy format), for example:

```text
DATABASE_URL=postgresql://username:password@localhost:5433/turkcell_db
```

2. Apply `gamification_database.sql` to your database manually (see `backend/database/README.md` for examples using `psql` or Docker).
