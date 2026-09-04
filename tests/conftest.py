from datetime import datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.database import engine, ensure_database


def mysql_available() -> bool:
    try:
        ensure_database()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except (SQLAlchemyError, ValueError, OSError):
        return False


requires_mysql = pytest.mark.skipif(not mysql_available(), reason="MySQL credentials not configured")
