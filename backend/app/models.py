from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from .database import Base


class ClassificationHistory(Base):
    """분류 작업 이력"""
    __tablename__ = "classification_history"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    result_path = Column(String, nullable=True)
    sheet_name = Column(String, nullable=False)
    column_name = Column(String, nullable=False)
    status = Column(String, default="processing")  # processing, completed, failed
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class UserSettings(Base):
    """사용자 설정"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    openai_api_key = Column(String, nullable=True)
    openai_base_url = Column(String, default="https://api.openai.com/v1")
    model_name = Column(String, default="gpt-4o-mini")
    sheet_name = Column(String, default="일보_Worst55")
    column_name = Column(String, default="Issue")
    prompt = Column(Text, nullable=True)
    few_shot_examples = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
