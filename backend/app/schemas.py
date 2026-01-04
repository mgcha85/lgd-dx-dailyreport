from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SettingsBase(BaseModel):
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4o-mini"
    sheet_name: str = "일보_Worst55"
    column_name: str = "Issue"
    prompt: Optional[str] = None
    few_shot_examples: Optional[str] = None


class SettingsUpdate(SettingsBase):
    pass


class SettingsResponse(SettingsBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    message: str


class ClassificationRequest(BaseModel):
    file_path: str
    sheet_name: str = "일보_Worst55"
    column_name: str = "Issue"
    prompt: str = "다음 Issue 내용을 분석하여 불량명, 설비명, 조치내용을 JSON 형식으로 추출해주세요."


class ClassificationResponse(BaseModel):
    history_id: int
    filename: str
    status: str
    total_rows: int
    processed_rows: int
    failed_rows: int
    result_path: Optional[str] = None
    message: str


class HistoryResponse(BaseModel):
    id: int
    filename: str
    sheet_name: str
    column_name: str
    status: str
    total_rows: int
    processed_rows: int
    failed_rows: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ClassificationResult(BaseModel):
    불량명: str = ""
    설비명: str = ""
    조치내용: str = ""
