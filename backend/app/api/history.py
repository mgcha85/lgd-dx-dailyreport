from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import ClassificationHistory
from ..schemas import HistoryResponse

router = APIRouter()


@router.get("/history", response_model=List[HistoryResponse])
def get_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    분류 작업 이력 조회
    
    Args:
        skip: 건너뛸 레코드 수
        limit: 조회할 최대 레코드 수
    """
    histories = db.query(ClassificationHistory)\
        .order_by(ClassificationHistory.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return histories


@router.get("/history/{history_id}", response_model=HistoryResponse)
def get_history_by_id(
    history_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 분류 작업 이력 조회
    """
    history = db.query(ClassificationHistory)\
        .filter(ClassificationHistory.id == history_id)\
        .first()
    
    if not history:
        raise HTTPException(status_code=404, detail="이력을 찾을 수 없습니다.")
    
    return history
