from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./data/app.db"
    
    # File Upload
    upload_dir: str = "/app/data/uploads"
    results_dir: str = "/app/data/results"
    max_upload_size: int = 52428800  # 50MB
    
    # OpenAI defaults (can be overridden by user settings)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    
    # Default settings
    default_sheet_name: str = "일보_Worst55"
    default_column_name: str = "Issue"
    default_prompt: str = "다음 Issue 내용을 분석하여 불량명, 설비명, 조치내용을 JSON 형식으로 추출해주세요."
    
    # Mock mode (for testing without actual OpenAI API)
    mock_llm: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Create directories if they don't exist
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.results_dir).mkdir(parents=True, exist_ok=True)
