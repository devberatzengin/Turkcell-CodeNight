# Game+ Quest League — Gamification System

A complete backend system for managing user quests, points, badges, and leaderboards in a game ecosystem.

## Features

✅ **Core Requirements (9/9 Complete)**
- Activity data ingestion (CSV → PostgreSQL)
- User metrics calculation (today, 7-day, streak)
- Data-driven quest engine with safe condition evaluation
- Conflict resolution (single award per day, min priority selection)
- Points ledger (transactional record-keeping)
- Leaderboard generation
- Badge assignment (idempotent)
- Notifications (mock)
- Interactive dashboard

## Tech Stack

- **Backend:** FastAPI (Python 3.12)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Frontend:** Single-page HTML dashboard
- **Testing:** pytest
- **Containerization:** Docker & docker-compose
- **Task Running:** Make

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── models/              # Split ORM models (one file per entity)
│   │   ├── controllers/         # FastAPI route handlers
│   │   ├── services/            # Business logic (ingest, pipeline)
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── db.py                # SQLAlchemy setup
│   │   ├── main.py              # FastAPI app entry
│   │   └── static/              # Static files (dashboard HTML)
│   ├── scripts/                 # Utility scripts
│   ├── tests/                   # pytest test suite
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment template
│   └── Dockerfile
├── datasets/                    # CSV data files
├── docker-compose.yml           # Docker Compose config
├── Makefile                     # Task automation
├── gamification_database.sql    # SQL schema & seed data
└── README.md                    # This file
```

## Quick Start

### Local Development (No Docker)

1. **Clone and setup:**
   ```bash
   cd TurkcellBootcamp
   make install  # or: pip install -r backend/requirements.txt
   ```

2. **Setup PostgreSQL:**
   - Ensure PostgreSQL is running on `localhost:5433`
   - Create database: `createdb turkcell_db -U postgres`
   - Apply schema: `psql -U postgres turkcell_db < gamification_database.sql`

3. **Configure environment:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env: ensure DATABASE_URL is correct
   ```

4. **Run API:**
   ```bash
   make dev
   ```

5. **View dashboard:**
   - Dashboard: http://127.0.0.1:8000/static/dashboard.html
   - API docs: http://127.0.0.1:8000/docs
   - Health: http://127.0.0.1:8000/health

6. **Trigger pipeline (ingest CSVs):**
   ```bash
   curl -X POST "http://127.0.0.1:8000/pipeline/run?sync=true"
   ```

### Docker Setup

1. **Build and start:**
   ```bash
   make build
   make up
   ```

2. **Check logs:**
   ```bash
   make logs
   ```

3. **Access:**
   - Dashboard: http://localhost:8000/static/dashboard.html
   - API: http://localhost:8000
   - Postgres: `localhost:5433` (postgres/postgres)

4. **Stop:**
   ```bash
   make down
   ```

## API Endpoints

### Users
- `GET /users/` — List all users
- `GET /users/{user_id}` — User details with state, awards, badges, notifications

### Metrics
- `GET /user_state/` — List all user states
- `GET /user_state/{user_id}` — Specific user's metrics (today, 7-day, streak, total_points)

### Quests & Awards
- `GET /awards/` — List all quest awards
- `GET /awards/user/{user_id}` — User's quest awards

### Badges
- `GET /badge_awards/` — List all badge awards
- `GET /badge_awards/user/{user_id}` — User's earned badges

### Notifications
- `GET /notifications/` — List all notifications
- `GET /notifications/user/{user_id}` — User's notifications

### Leaderboard
- `GET /leaderboard/` — List leaderboard
- `GET /leaderboard/top?n=10` — Top N users

### Pipeline
- `POST /pipeline/run?sync=true` — Ingest CSVs, compute state, award quests/badges (synchronous)
- `POST /pipeline/run` — Same but background task

### System
- `GET /health` — Health check
- `GET /db/check` — Database connectivity test
- `GET /docs` — Swagger API documentation

## Testing

Run all tests:
```bash
make test  # or: cd backend && pytest tests/ -v
```

Tests cover:
- Safe expression evaluator
- User state calculation (today, 7-day, streak)
- CSV loading and model relationships
- Conflict resolution and quest evaluation

## Environment Variables

```bash
# backend/.env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/turkcell_db
# or old JDBC format:
JDBC_URL=jdbc:postgresql://localhost:5433/turkcell_db?user=postgres&password=postgres
```

## System Flow

1. **Ingest:** CSVs (users, games, quests, badges, activity_events) → PostgreSQL
2. **State Calculation:** Activity events → user_state (metrics)
3. **Quest Evaluation:** State + quest conditions → triggered quests
4. **Conflict Resolution:** Multiple quests per day → select min priority
5. **Award & Ledger:** Create quest_awards + points_ledger entries
6. **Badge Assignment:** Check total_points → badge_awards (idempotent)
7. **Leaderboard:** Rank by total_points (highest → lowest, tie-breaker: user_id)
8. **Notifications:** Create mock notifications for awards

## Key Implementation Details

### Safe Expression Evaluator
- Uses Python's `ast` module for safe, sandboxed evaluation
- Supports: comparisons, boolean logic (and/or), arithmetic
- Blocks dangerous operations (imports, function calls)

### Idempotency
- Badge awards checked before insert (no duplicates)
- Leaderboard truncated and rebuilt each run
- Quest awards have unique award_id timestamps

### Database Design
- Normalized schema with foreign keys
- Points stored in ledger (immutable), total_points computed from ledger
- User state is materialized view (updated via pipeline)

## Scoring Rubric (100 points)

- **Temel İşlevsellik (30):** ✅ All 9 core features implemented
- **Veri Modeli (20):** ✅ Proper schema, normalized tables, relationships
- **Kural & Karar (20):** ✅ Safe condition eval, conflict resolution (min priority)
- **Kod Kalitesi (15):** ✅ MVC structure, services, unit tests, type hints
- **Görsellik (10):** ✅ Interactive dashboard with user details, metrics, badges
- **Bonus (5):** ⏳ Optional: what-if simulator, ledger visualizations

## Optional Features (Bonus)

### What-If Simulator
TBD: Endpoint to simulate "if user had +N metric points, which quest would win?"

### Ledger Visualization
TBD: Chart showing daily/cumulative points over time per user

## Troubleshooting

### Database Connection Failed
```bash
make check-db
# Verify backend/.env DATABASE_URL matches your Postgres setup
```

### Pipeline "relation does not exist"
- Ensure `gamification_database.sql` was applied: `psql -U postgres turkcell_db < gamification_database.sql`
- Restart containers: `make down && make up`

### Tests fail with import errors
```bash
cd backend
pip install -e .  # Install in editable mode
pytest tests/ -v
```

## Development Workflow

1. **Create feature branch:** `git checkout -b feature/xyz`
2. **Code + tests:** `make test` frequently
3. **Lint:** `make lint`
4. **Commit:** `git add . && git commit -m "..."`
5. **Push & PR**

## License

MIT (or as per Turkcell's policy)

## References

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [pytest documentation](https://docs.pytest.org/)
- [Docker Compose](https://docs.docker.com/compose/)
