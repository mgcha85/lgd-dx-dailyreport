from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import UserSettings
from ..schemas import SettingsUpdate, SettingsResponse
from ..config import settings as app_settings

router = APIRouter()


@router.get("/settings", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """
    현재 사용자 설정 조회
    """
    # 첫 번째 설정 레코드 조회 (단일 사용자 가정)
    user_settings = db.query(UserSettings).first()
    
    if not user_settings:
        # 설정이 없으면 기본값으로 생성
        user_settings = UserSettings(
            openai_api_key="",
            openai_base_url=app_settings.openai_base_url,
            model_name=app_settings.openai_model,
            sheet_name=app_settings.default_sheet_name,
            column_name=app_settings.default_column_name,
            few_shot_examples=""
        )
        db.add(user_settings)
        db.commit()
        db.refresh(user_settings)
    
    return user_settings


@router.put("/settings", response_model=SettingsResponse)
def update_settings(
    settings_update: SettingsUpdate,
    db: Session = Depends(get_db)
):
    """
    사용자 설정 업데이트
    """
    user_settings = db.query(UserSettings).first()
    
    if not user_settings:
        # 설정이 없으면 새로 생성
        user_settings = UserSettings(**settings_update.model_dump())
        db.add(user_settings)
    else:
        # 기존 설정 업데이트
        for key, value in settings_update.model_dump().items():
            setattr(user_settings, key, value)
    
    db.commit()
    db.refresh(user_settings)
    
    return user_settings
