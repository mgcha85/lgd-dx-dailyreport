from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import UserSettings
from ..schemas import SettingsUpdate, SettingsResponse
from ..config import settings as app_settings
import requests

router = APIRouter()


@router.post("/settings/check-models")
async def check_available_models(
    base_url: str = Body(..., embed=True),
    api_key: str = Body(..., embed=True)
):
    """
    제공된 Base URL과 API Key로 모델 목록을 조회합니다.
    """
    try:
        # 마지막 슬래시 제거
        if base_url.endswith("/"):
            base_url = base_url[:-1]
            
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/models", headers=headers, timeout=5)
        
        response.raise_for_status()
        data = response.json()
        
        # OpenAI 표준 포맷: {"data": [{"id": "model-id", ...}, ...]}
        models = [model["id"] for model in data.get("data", [])]
        return {"models": models}
        
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"모델 목록을 불러오는데 실패했습니다: {str(e)}"
        )


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
            prompt=app_settings.default_prompt,
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
