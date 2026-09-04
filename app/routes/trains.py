from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.train import TrainCreate, TrainRead
from app.services import maintenance_service as svc

router = APIRouter(prefix="/api/trains", tags=["Trains"])


@router.get("", response_model=list[TrainRead])
def list_trains(db: Session = Depends(get_db)):
    return svc.list_trains(db)


@router.post("", response_model=TrainRead, status_code=201)
def create_train(payload: TrainCreate, db: Session = Depends(get_db)):
    return svc.create_train(db, payload)


@router.get("/{train_id}", response_model=TrainRead)
def get_train(train_id: int, db: Session = Depends(get_db)):
    return svc.get_train(db, train_id)
