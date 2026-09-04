from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.database import engine, ensure_database


def test_mysql_connection() -> None:
    """Verify SQLAlchemy can reach MySQL and run a trivial query."""
    try:
        ensure_database()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
    except OperationalError as exc:
        raise AssertionError(
            "MySQL rejected the connection. Set a valid DATABASE_URL in .env "
            "(username/password for the local MySQL 5.0 server)."
        ) from exc
    except SQLAlchemyError as exc:
        raise AssertionError("MySQL connection failed. Check DATABASE_URL in .env.") from exc
    assert result == 1
