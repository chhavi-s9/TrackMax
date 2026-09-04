from typing import Any, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.utils.time_utils import enum_value

T = TypeVar("T")


def get_or_404(db: Session, model: Type[T], entity_id: int, name: str) -> T:
    obj = db.get(model, entity_id)
    if obj is None:
        raise NotFoundError(name, entity_id)
    return obj


def list_all(db: Session, model: Type[T], limit: int = 500) -> list[T]:
    return list(db.scalars(select(model).limit(limit)).all())


def apply_updates(obj: Any, data: dict[str, Any]) -> Any:
    for key, value in data.items():
        if value is None:
            continue
        setattr(obj, key, enum_value(value) if hasattr(value, "value") else value)
    return obj


def commit_or_conflict(db: Session, obj: T, message: str) -> T:
    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictError(message)


def dump_enums(data: dict[str, Any]) -> dict[str, Any]:
    return {k: enum_value(v) if v is not None else None for k, v in data.items()}
