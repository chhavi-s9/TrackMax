# Railway block planning backend (SIH 2026 MVP)

Backend for **AI-powered automatic block planning** to coordinate railway maintenance blocks around train operations.

This repository uses **synthetic/demo data only**. It is not real Indian Railways operational data.

The product name has not been decided. This folder is the technical project directory.

## What it does

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

On this Windows machine Anaconda `Scripts` may not be on `PATH`. Use:

`C:\Users\uk_just_KD\anaconda3\python.exe -m pip install -r requirements.txt`

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
