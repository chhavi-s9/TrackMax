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
