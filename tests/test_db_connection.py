from tests.conftest import requires_mysql
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.database import engine, ensure_database


@requires_mysql
def test_mysql_connection() -> None:
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
