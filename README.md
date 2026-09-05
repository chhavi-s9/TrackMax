# Backend fixes for SIH block-planning MVP

Repaired files included:
- `app/main.py`
- `app/database.py`
- `app/optimizer/block_optimizer.py`
- supporting copied files under `app/`

Key fixes:
1. Standard FastAPI entrypoint is now `app.main:app` instead of relying on `main(4).py`.
2. Database engine/session initialization is lazy, so importing the app does not require the database to already exist.
3. Database creation is performed before the application engine is initialized.
4. CP-SAT `UNKNOWN` is no longer mislabeled as `INFEASIBLE`.
5. The optimizer no longer attempts to read solver variable values when CP-SAT returned `UNKNOWN`.
6. CORS is configured without `allow_credentials=True` together with wildcard origins.
7. Shutdown disposes the SQLAlchemy engine cleanly.

Important: the uploaded set does not contain `app/routes` (or the rest of the API/model/ML modules). Therefore this patch is syntax-checked, but a complete end-to-end FastAPI startup and API test cannot be certified until those modules are present.

Run from the project root:
`uvicorn app.main:app --reload`

Then check:
`GET /health`
`GET /docs`

1. Unifies mock TMS / SMMS / TDMS maintenance tasks in one MySQL database
2. Ranks work with a **Random Forest** (risk/priority only)
3. Finds feasible block windows around train movements
4. Schedules blocks with **Google OR-Tools CP-SAT** (the optimizer)
5. Compares manual vs coordinated vs AI what-if scenarios
6. Re-ranks and reschedules when weather changes

## Requirements

- Python 3.11+ (this machine: Anaconda 3.12.7)
- MySQL (this machine currently runs MySQL 5.0.45)

Project directory: `D:\railway-block-planning`

## Setup

Work from this folder:

```bash
cd D:\railway-block-planning
```

1. Copy `.env.example` to `.env` and set `DATABASE_URL` (do not commit `.env`).

```text
DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@localhost:3306/railway_block_planning
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```


3. Create the database schema:

```bash
python -m alembic upgrade head
```

4. Seed synthetic demo data and train the demonstration risk model:

```bash
python -m seed.seed_data
```

5. Run the API:

```bash
python -m uvicorn app.main:app --reload
```

- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: http://127.0.0.1:8000/health

## Core endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/maintenance-overview` | Unified TMS/SMMS/TDMS + corridor view |
| GET | `/api/prioritized-tasks` | Ranked list (ML + rules) |
| GET | `/api/weekly-plan` | CP-SAT week plan |
| GET | `/api/monthly-plan` | High-level outlook |
| GET | `/api/scenario` | Manual / coordinated / AI comparison |
| POST | `/api/weather/reschedule` | Weather-aware reschedule |
| POST | `/api/optimizer/run` | Single-day CP-SAT run |
| POST | `/api/blocks/validate` | Conflict check |
| GET | `/api/windows` | Candidate block windows |

## Tests

```bash
python -m pytest
```

MySQL-backed tests are skipped if `DATABASE_URL` cannot authenticate.

## MySQL 5.0 note

The local server is MySQL **5.0.45**. The schema avoids `utf8mb4`, `JSON` columns, and `DATETIME(6)`.
