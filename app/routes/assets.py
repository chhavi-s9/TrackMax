from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate
from app.services import maintenance_service as svc

router = APIRouter(prefix="/api/assets", tags=["Assets"])


@router.get("", response_model=list[AssetRead])
def list_assets(section: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    return svc.list_assets(db, section=section)


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    return svc.get_asset(db, asset_id)


@router.post("", response_model=AssetRead, status_code=201)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    return svc.create_asset(db, payload)


@router.put("/{asset_id}", response_model=AssetRead)
def update_asset(asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db)):
    return svc.update_asset(db, asset_id, payload)


@router.delete("/{asset_id}", status_code=204)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    svc.delete_asset(db, asset_id)
    return Response(status_code=204)
