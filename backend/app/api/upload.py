from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from ..config import settings
from ..schemas import FileUploadResponse
from ..services.file_processor import (
    is_allowed_file,
    save_upload_file,
    create_unique_filename
)
from ..core.preprocessor import run_preprocessing_pipeline

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    파일 업로드 엔드포인트
    
    엑셀 또는 PPTX 파일을 업로드하여 임시 저장
    """
    # 파일 확장자 검증
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않는 파일 형식입니다. 허용 형식: .xlsx, .xls, .pptx, .xlsb"
        )
    
    # 고유 파일명 생성
    upload_dir = Path(settings.upload_dir)
    file_path = create_unique_filename(file.filename, upload_dir)
    
    try:
        # 파일 저장
        await save_upload_file(file, file_path)
        
        # 전처리 파이프라인 실행
        # settings에 기본 시트 이름이 있을 수 있지만, 현재는 기본값으로 처리하거나 추후 파라미터로 받을 수 있음
        # 여기서는 파일 자체를 전처리하여 덮어쓰거나 새 파일 생성
        processed_path = run_preprocessing_pipeline(file_path, sheet_name=settings.default_sheet_name)
        
        return FileUploadResponse(
            filename=file.filename, # 원본 유저 파일명 유지
            file_path=str(processed_path), # 처리된 파일 경로 반환
            message="파일이 성공적으로 업로드 및 전처리되었습니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}"
        )
