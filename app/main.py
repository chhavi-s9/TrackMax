from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.config import get_settings
from app.database import ensure_database, get_db, initialize_database
from app.routes import ALL_ROUTERS

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.auto_create_database:
        try:
            ensure_database()
        except (SQLAlchemyError, ValueError) as exc:
            raise RuntimeError("Could not connect to MySQL or create the application database.") from exc
    try:
        initialize_database()
        yield
    finally:
        # SQLAlchemy engines are intentionally disposed on shutdown when initialized.
        from app.database import dispose_engine
        dispose_engine()


app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend MVP for AI-powered automatic block planning to maximize "
        "asset availability for train operations. Demo/synthetic data only — "
        "not real Indian Railways operational data."
    ),
    version="0.2.1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in ALL_ROUTERS:
    app.include_router(router)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(_request: Request, _exc: SQLAlchemyError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "A database error occurred."})


@app.get("/health", tags=["Health"])
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok", "database": "connected"}
