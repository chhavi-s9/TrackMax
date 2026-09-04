# Railway block planning backend (SIH 2026 MVP)

Backend for **AI-powered automatic block planning** to coordinate railway maintenance blocks around train operations.

This repository uses **synthetic/demo data only**. It is not real Indian Railways operational data.

The product name has not been decided. This folder is the technical project directory.

## Requirements

- Python 3.11+ (this machine: Anaconda 3.12.7)
- MySQL (this machine currently runs MySQL 5.0.45)

## Setup

1. Copy `.env.example` to `.env` and set `DATABASE_URL` (do not commit `.env`).
2. Install dependencies (Anaconda base is used for this MVP):

```bash
python -m pip install -r requirements.txt
```

3. Create / migrate the database (schema arrives in Phase 3):

```bash
python -m alembic upgrade head
```

4. Run the API:

```bash
python -m uvicorn app.main:app --reload
```

- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: http://127.0.0.1:8000/health

On this Windows machine, Anaconda `Scripts` may not be on `PATH`. Use:

`C:\Users\uk_just_KD\anaconda3\python.exe -m uvicorn app.main:app --reload`

## MySQL 5.0 note

The local server is MySQL **5.0.45**. The schema avoids features that server cannot support (`utf8mb4`, `JSON` columns, `DATETIME(6)`).
