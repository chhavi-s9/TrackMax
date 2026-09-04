from fastapi import HTTPException


class NotFoundError(HTTPException):
    def __init__(self, entity: str, entity_id: int) -> None:
        super().__init__(status_code=404, detail=f"{entity} {entity_id} not found")


class ConflictError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=409, detail=detail)


class BadRequestError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=400, detail=detail)


class ModelUnavailableError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=503,
            detail="Risk model is unavailable. Train it with: python -m app.ml.train",
        )
