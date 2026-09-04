import re
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

_DB_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")


class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy 2.x models (added in Phase 3)."""


def _build_engine(url: str) -> Engine:
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=3600,
        future=True,
    )


def get_engine() -> Engine:
    return _build_engine(get_settings().database_url)


engine = get_engine()
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_database() -> None:
    """Create the application database if it does not already exist.

    Connects to the MySQL system schema so the app database can be created
    on a fresh install. Safe to call on every startup.
    """
    url = make_url(get_settings().database_url)
    db_name = url.database
    if not db_name or not _DB_NAME_RE.fullmatch(db_name):
        raise ValueError("DATABASE_URL must include a valid database name")

    admin_url = url.set(database="mysql")
    admin_engine = _build_engine(admin_url.render_as_string(hide_password=False))
    try:
        with admin_engine.begin() as conn:
            # MySQL 5.0: utf8 (3-byte). Avoid utf8mb4 / DATETIME(6) / JSON.
            conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                    "CHARACTER SET utf8 COLLATE utf8_general_ci"
                )
            )
    finally:
        admin_engine.dispose()
